FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Importante: impostare PYTHONPATH per trovare i moduli
ENV PYTHONPATH=/app/src
ENV FLASK_APP=src/app.py

EXPOSE 5001

CMD ["python", "src/app.py"]