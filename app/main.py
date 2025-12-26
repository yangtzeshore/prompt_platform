from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database, engine
import random
from . import evaluator

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)

@app.get("/")
def read_root():
    return {"status": "Prompt Platform is running"}

# --- Snippet 管理 ---
@app.post("/v1/snippets")
def save_snippet(name: str, content: str, db: Session = Depends(database.get_db)):
    db_snippet = db.query(models.Snippet).filter(models.Snippet.name == name).first()
    if db_snippet:
        db_snippet.content = content
    else:
        db_snippet = models.Snippet(name=name, content=content)
        db.add(db_snippet)
    db.commit()
    return {"status": "success"}

# 1. 注册/更新提示词
@app.post("/v1/prompts")
def create_prompt(prompt: schemas.PromptCreate, db: Session = Depends(database.get_db)):
    # 如果设置了别名，先把该名称下旧的相同别名清除（保证别名唯一性）
    if prompt.alias:
        db.query(models.Prompt).filter(
            models.Prompt.name == prompt.name, 
            models.Prompt.alias == prompt.alias
        ).update({"alias": None})
    
    db_prompt = models.Prompt(**prompt.dict())
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

# --- 增强版渲染接口 ---
@app.post("/v1/prompts/render")
def render_prompt(req: schemas.RenderRequest, db: Session = Depends(database.get_db)):
    # 查找逻辑（同前）
    query = db.query(models.Prompt).filter(models.Prompt.name == req.name)
    target = query.filter(models.Prompt.version == req.version).first() if req.version \
             else query.filter(models.Prompt.alias == req.alias).first()
    
    if not target:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # 执行增强渲染
    rendered_text, tokens, latency = engine.render_template_with_snippets(
        db, target.content, req.variables
    )

    # 异步落盘日志（简单实现直接写库）
    log = models.RenderLog(
        prompt_name=target.name,
        version=target.version,
        tokens=tokens,
        latency_ms=latency
    )
    db.add(log)
    db.commit()

    return {
        "rendered_content": rendered_text,
        "metrics": {
            "tokens": tokens,
            "latency_ms": round(latency, 2)
        },
        "info": {"version": target.version, "name": target.name}
    }

# --- 简单统计接口 ---
@app.get("/v1/stats")
def get_stats(db: Session = Depends(database.get_db)):
    total_renders = db.query(models.RenderLog).count()
    # 可以在这里做更多复杂的聚合查询
    return {"total_renders": total_renders}

# --- 1. AB 测试渲染接口 ---
@app.post("/v1/prompts/render-ab")
def render_ab(experiment_name: str, variables: dict, db: Session = Depends(database.get_db)):
    exp = db.query(models.Experiment).filter(models.Experiment.name == experiment_name).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # 简单的随机分流逻辑
    chosen_version = exp.version_a if random.random() < exp.weight_a else exp.version_b
    
    # 调用之前的渲染逻辑
    target = db.query(models.Prompt).filter(
        models.Prompt.name == exp.prompt_name, 
        models.Prompt.version == chosen_version
    ).first()
    
    rendered_text, tokens, latency = engine.render_template_with_snippets(db, target.content, variables)
    
    return {
        "version": chosen_version,
        "rendered_content": rendered_text,
        "experiment_id": exp.id
    }

# --- 2. 自动化评价接口 ---
@app.post("/v1/evaluate")
def evaluate_prompt(prompt_id: int, model_output: str, criteria: str, db: Session = Depends(database.get_db)):
    prompt = db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # 调用千问进行打分
    result = evaluator.llm_judge(prompt.content, model_output, criteria)
    return {"evaluation": result}
