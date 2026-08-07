FROM python:3.12-slim
WORKDIR /src

ENV UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y netcat-openbsd && \
    pip install uv

COPY . .

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

RUN chmod +x wait-for-it.sh start.sh
EXPOSE 8000

CMD ["./wait-for-it.sh", "arceus_db:5432", "./start.sh", ".venv/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
