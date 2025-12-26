from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from .database import Base
from datetime import datetime

class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    content = Column(Text)
    version = Column(String)
    alias = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    description = Column(Text, nullable=True) # 新增这一行

class Snippet(Base):
    __tablename__ = "snippets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # 唯一标识符，如 "json_format"
    content = Column(Text)                         # 片段内容

class RenderLog(Base):
    __tablename__ = "render_logs"
    id = Column(Integer, primary_key=True, index=True)
    prompt_name = Column(String)
    version = Column(String)
    tokens = Column(Integer)        # 预估 Token 数
    latency_ms = Column(Float)      # 渲染耗时
    created_at = Column(DateTime, default=datetime.now)

# 增加一个实验表
class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    prompt_name = Column(String)
    version_a = Column(String)
    version_b = Column(String)
    weight_a = Column(Float, default=0.5) # A版本权重，如 0.2 表示 20% 流量
