import os
from openai import OpenAI

# 建议在 docker-compose 中通过环境变量传入 API_KEY
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"), 
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def llm_judge(prompt_content: str, output: str, criteria: str):
    """
    使用千问作为裁判，对输出进行打分
    """
    judge_prompt = f"""
    你是一个严谨的裁判。请根据以下评价标准，给模型的输出打分（0-10分）。
    
    【评价标准】：{criteria}
    【提示词】：{prompt_content}
    【模型输出】：{output}
    
    请直接返回JSON格式：{{"score": 分数, "reason": "简短的理由"}}
    """
    
    response = client.chat.completions.create(
        model="qwen-plus", # 免费额度通常支持 qwen-plus/turbo
        messages=[{"role": "user", "content": judge_prompt}],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content
