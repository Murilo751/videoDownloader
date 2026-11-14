FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api.py db.py cli.py ./
COPY tests ./tests
ENV PYTHONUNBUFFERED=1
CMD ["python", "api.py"]
