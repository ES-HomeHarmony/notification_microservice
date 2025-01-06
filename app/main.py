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
            if action == "expense_created":
                if user_data:
                    process_expense_created(user_data)
            if action == "new_issue":
                if user_data:
                    process_new_issue(user_data)
            if action == "tenant_paid":
                if user_data:
                    process_tenant_paid(user_data)
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
    print("Contract uploaded")
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

def process_expense_created(expense_data):
    print(f"Recebendo dados de despesa: {expense_data}")
    
    try:
        # Validar a estrutura da mensagem

        expense_details = expense_data.get("expense_details")
        users = expense_data.get("users")

        if not expense_details:
            raise ValueError("Detalhes da despesa não encontrados.")
        if not users or len(users) == 0:
            raise ValueError("Nenhum usuário encontrado na mensagem.")

        print("Dados validados com sucesso.")
        
        # Dados da despesa
        title = expense_details.get("title", "Sem título")
        amount = str(expense_details.get("amount", "0.0"))
        description = expense_details.get("description", "Sem descrição")
        deadline_date = expense_details.get("deadline_date", "Sem data")
        subject = "Expense Created!"

        print(f"Detalhes da despesa: título={title}, valor={amount}, descrição={description}, data limite={deadline_date}")
        
        # Carregar o template do e-mail
        template_path = "templates/expense.html"
        with open(template_path, 'r', encoding='utf-8') as file:
            html_template = file.read()

        for user in users:
            print(f"Processando usuário: {user}")
            name = user.get("name", "Usuário desconhecido")
            email = user.get("email")

            if not email:
                print(f"Usuário {name} não tem um e-mail válido, ignorando.")
                continue

            # Personaliza o HTML para o usuário
            html_message = html_template.replace("{{name}}", name)
            html_message = html_message.replace("{{title}}", title)
            html_message = html_message.replace("{{amount}}", amount)
            html_message = html_message.replace("{{deadline_date}}", deadline_date)

          

            # Envia o e-mail
            send_email(email, subject, html_message)
            print(f"E-mail enviado para {email}")
    
    except Exception as e:
        print(f"Erro ao processar expense_created: {e}")

def process_new_issue(issue_data):
    print(f"Recebendo dados de nova issue: {issue_data}")
    try:
        # Validar a estrutura da mensagem

        issue = issue_data.get("issue")
        house_name = issue_data.get("house_name")
        tenant_name = issue_data.get("tenant_name")
        users = issue_data.get("users")

        if not issue:
            raise ValueError("Detalhes da issue não encontrados.")
        if not users or len(users) == 0:
            raise ValueError("Nenhum usuário encontrado na mensagem.")

        print("Dados validados com sucesso.")
        
        # Dados da issue
        title = issue.get("title", "Sem título")
        description = issue.get("description", "Sem descrição")
        status = issue.get("status", "Sem status")
        priority = issue.get("priority", "Sem prioridade")
        subject = "New Issue Created!"

        print(f"Detalhes da issue: título={title}, descrição={description}, status={status}, prioridade={priority}")
        
        # Carregar o template do e-mail
        template_path = "templates/issue.html"
        with open(template_path, 'r', encoding='utf-8') as file:
            html_template = file.read()

        for user in users:
            print(f"Processando usuário: {user}")
            name = user.get("name", "Usuário desconhecido")
            email = user.get("email")

            if not email:
                print(f"Usuário {name} não tem um e-mail válido, ignorando.")
                continue

            # Personaliza o HTML para o usuário
            html_message = html_template.replace("{{name}}", name)
            html_message = html_message.replace("{{title}}", title)
            html_message = html_message.replace("{{description}}", description)
            html_message = html_message.replace("{{status}}", status)
            html_message = html_message.replace("{{priority}}", priority)
            html_message = html_message.replace("{{house_name}}", house_name)
            html_message = html_message.replace("{{tenant_name}}", tenant_name)

            # Envia o e-mail
            send_email(email, subject, html_message)
            print(f"E-mail enviado para {email}")
            
    except Exception as e:
        print(f"Erro ao processar expense_created: {e}")

def process_tenant_paid(tenant_data):
    print(f"Recebendo dados de pagamento de inquilino: {tenant_data}")
    try:
        # Validar a estrutura da mensagem

        email = tenant_data.get("email")
        name = tenant_data.get("name")
        tenant_name = tenant_data.get("tenant_name")
        expense_name = tenant_data.get("expense_name")
        amount = tenant_data.get("amount")
        house_name = tenant_data.get("house_name")

        if not email:
            raise ValueError("Email do locador não encontrado.")
        print("Dados validados com sucesso.")
        
        # Dados do pagamento
        subject = "Tenant Payment Received!"

        print(f"Detalhes do pagamento: locador={name}, inquilino={tenant_name}, despesa={expense_name}, valor={amount}, casa={house_name}")
        
        # Carregar o template do e-mail
        template_path = "templates/tenant_payment.html"
        with open(template_path, 'r', encoding='utf-8') as file:
            html_template = file.read()

        # Personaliza o HTML para o usuário
        html_message = html_template.replace("{{name}}", name)
        html_message = html_message.replace("{{tenant_name}}", tenant_name)
        html_message = html_message.replace("{{expense_name}}", expense_name)
        html_message = html_message.replace("{{amount}}", str(amount))
        html_message = html_message.replace("{{house_name}}", house_name)

        # Envia o e-mail
        send_email(email, subject, html_message)
        print(f"E-mail enviado para {email}")
            
    except Exception as e:
        print(f"Erro ao processar tenant_paid: {e}")

    
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