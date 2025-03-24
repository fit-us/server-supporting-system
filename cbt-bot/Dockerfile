FROM python:3.11-slim

# 작업 디렉터리 생성 및 설정
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]