FROM python:3.12-slim
WORKDIR /app/
COPY requirements.txt .
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/* \
	&& pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
RUN chmod +x /app/wait-for-it.sh
CMD ["/app/wait-for-it.sh", "db:5432", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]