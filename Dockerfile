FROM python:3.13-alpine

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Ensure SQLite data directory exists
RUN mkdir -p /app/data
COPY data/*.sql /app/data/

# Install dependencies globally inside the container
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy application source code
COPY src/ /app/src/

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
