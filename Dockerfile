# Dockerfile
FROM python:3.11-slim

# Install uv
RUN pip install --upgrade pip && pip install uv

# Set working directory
WORKDIR /app

# Copy source files
COPY . .

# Install base + editable project
RUN uv pip install --system --editable .

# Start FastAPI app
CMD ["uvicorn", "llmops.main:app", "--host", "0.0.0.0", "--port", "8000"]
