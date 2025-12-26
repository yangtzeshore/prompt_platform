import time
import tiktoken
from jinja2 import Template
from sqlalchemy.orm import Session
from .models import Snippet

# 默认使用 cl100k_base 分词器 (GPT-4)
encoding = tiktoken.get_encoding("cl100k_base")

def render_template_with_snippets(db: Session, template_str: str, variables: dict):
    start_time = time.time()
    
    # 1. 从数据库获取所有 Snippets 并转化为字典
    snippets = db.query(Snippet).all()
    snippet_dict = {f"snippet_{s.name}": s.content for s in snippets}
    
    # 2. 合并用户变量与 Snippets (Snippet 优先级较高，或前缀区分)
    combined_vars = {**variables, **snippet_dict}
    
    # 3. 渲染
    template = Template(template_str)
    rendered_text = template.render(**combined_vars)
    
    # 4. 计算指标
    latency = (time.time() - start_time) * 1000
    token_count = len(encoding.encode(rendered_text))
    
    return rendered_text, token_count, latency
