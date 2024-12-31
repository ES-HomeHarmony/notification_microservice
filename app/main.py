from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import smtplib
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente
load_dotenv(".env/development.env")

app = FastAPI()

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
        print(f"Erro ao enviar email: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar email: {e}")

# Endpoint para envio de email
@app.post("/send-email/")
async def send_email_endpoint(email: EmailRequest, background_tasks: BackgroundTasks):
    # Adiciona a tarefa de envio de email em segundo plano
    background_tasks.add_task(send_email, email.email_to, email.subject, email.html_message)
    return {"message": "Email enviado para o processamento em segundo plano."}
