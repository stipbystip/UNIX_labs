FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY producer.py .

# Для немедленного вывода логов в Docker
ENV PYTHONUNBUFFERED=1

CMD ["python", "producer.py"]
