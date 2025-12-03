FROM python:3.12-slim
WORKDIR /app/
COPY pyproject.toml .
RUN apt-get update && apt-get install -y netcat-openbsd
RUN pip install uv
RUN uv sync --no-cache
COPY . .
RUN chmod +x wait-for-it.sh
EXPOSE 8000
CMD ["./wait-for-it.sh", "db:5432", "uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]