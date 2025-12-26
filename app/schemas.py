from pydantic import BaseModel
from typing import Optional, Dict, Any

class PromptBase(BaseModel):
    name: str
    content: str
    version: str
    alias: Optional[str] = None
    description: Optional[str] = None

class PromptCreate(PromptBase):
    pass

class RenderRequest(BaseModel):
    name: str
    alias: Optional[str] = "prod" # 默认渲染生产环境别名
    version: Optional[str] = None # 如果传了 version，则优先按 version 找
    variables: Dict[str, Any] = {}
