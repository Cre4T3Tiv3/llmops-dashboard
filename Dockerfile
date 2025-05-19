# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv tool
RUN pip install --upgrade pip && pip install uv

# Copy project
COPY . /app

# Install dependencies from requirements.txt
RUN uv pip install -r requirements.txt --system

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
