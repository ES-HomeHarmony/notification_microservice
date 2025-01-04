from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import smtplib
from dotenv import load_dotenv
import os
from kafka import KafkaConsumer
import threading
import json

# Carrega as variáveis de ambiente
load_dotenv(".env/development.env")

app = FastAPI()

# Kafka consumer setup
invite_consumer = KafkaConsumer(
    'invite-request',
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    auto_offset_reset='earliest',
    group_id='email-notifications',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Modelo para requisição de envio de email
class EmailRequest(BaseModel):
    email_to: EmailStr
    subject: str
    html_message: str


# Função para envio de email usando smtplib
def send_email(email_to: str, subject: str, html_message: str):
    smtp_server = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    # Configuração da mensagem
    message = MIMEMultipart()
    message["From"] = formataddr(("Home Harmony", smtp_user))
    message["To"] = email_to
    message["Subject"] = subject
    message.attach(MIMEText(html_message, "html"))

    # Conectar ao servidor SMTP e enviar o email
    try:
        print("Conectando ao servidor SMTP...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Ativa o STARTTLS
            print("Autenticando...")
            server.login(smtp_user, smtp_pass)  # Autenticar
            print("Enviando email...")
            server.sendmail(smtp_user, email_to, message.as_string())  # Enviar email
            print("Email enviado com sucesso!")
    except Exception as e:
            error_message = f"Erro ao enviar email: {e}"
            print(error_message)
            raise ValueError(error_message)  # Substitui HTTPException para simplificar no teste

def process_invite_messages():
    print(f"Subscribed to topics: {invite_consumer.subscription()}")
    for message in invite_consumer:
        try:
            invite_data = message.value
            action = invite_data.get("action")
            user_data = invite_data.get("user_data")
            if action == "create_user":
                if user_data:
                    process_user_data(user_data)
            if action == "upload_contract":
                if user_data:
                    process_contract_data(user_data)
                
        except Exception:
            pass  # Ignora erros ao processar a mensagem

# Função para lógica de processamento dos dados do usuário
def process_user_data(user_data):
    name = user_data.get("name")
    email = user_data.get("email")
    subject="Welcome to Home Harmony!"
    # Personaliza o assunto e o corpo do e-mail
    template_path = "templates/invite.html"

    # Carrega o conteúdo do arquivo HTML
    with open(template_path, 'r', encoding='utf-8') as file:
        html_message = file.read()

    # Substitui as variáveis no template
    html_message = html_message.replace("{{name}}", name)
    send_email(email, subject, html_message)

def process_contract_data(contract_data):
    name = contract_data.get("name")
    email = contract_data.get("email")
    subject="Contract Uploaded!"
    # Personaliza o assunto e o corpo do e-mail
    template_path = "templates/contract.html"

    # Carrega o conteúdo do arquivo HTML
    with open(template_path, 'r', encoding='utf-8') as file:
        html_message = file.read()

    # Substitui as variáveis no template
    html_message = html_message.replace("{{name}}", name)
    send_email(email, subject, html_message)


# Endpoint para envio de email não é necessário mais pois o envio de email é feito na função process_invite_messages está só aqui para teste
# @app.post("/send-email/")
# async def send_email_endpoint(email: EmailRequest, background_tasks: BackgroundTasks):
#     # Adiciona a tarefa de envio de email em segundo plano
#     background_tasks.add_task(send_email, email.email_to, email.subject, email.html_message)
#     return {"message": "Email enviado para o processamento em segundo plano."}


@app.on_event("startup")
def startup_event():
    try:
        consumer_thread = threading.Thread(target=process_invite_messages, daemon=True)
        consumer_thread.start()
        print("Kafka consumer thread started.")       
        
    except Exception as e:
        print(f"Error starting Kafka consumer threads: {e}")