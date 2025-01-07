FROM --platform=linux/amd64 python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os requisitos e instala as dependências
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copia o código da aplicação
COPY ./app /app/app

# Configura variáveis de ambiente
ENV SMTP_USER=homeharmony2024es@gmail.com \
    SMTP_PASS='tsub thsu gpcc lgpc' \
    SMTP_HOST=smtp.gmail.com \
    SMTP_PORT=587 \
    KAFKA_BOOTSTRAP_SERVERS=b-1.mskcluster.l2ty7c.c2.kafka.eu-north-1.amazonaws.com:9092,b-2.mskcluster.l2ty7c.c2.kafka.eu-north-1.amazonaws.com:9092,b-3.mskcluster.l2ty7c.c2.kafka.eu-north-1.amazonaws.com:9092
                        
# Exponha a porta do microserviço
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]