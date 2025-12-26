FROM python:3.10-slim

WORKDIR /app

# 使用清华大学源加速安装
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# --reload 允许你在修改宿主机 app 文件夹下的代码时，容器自动重启应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
