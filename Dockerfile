FROM python:3.11-slim

WORKDIR /app

# Variaveis de Ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do codigo backend
COPY . .

# Expõe a porta do backend
EXPOSE 8000

# Executa o servidor Uvicorn FastAPI
CMD ["python", "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
