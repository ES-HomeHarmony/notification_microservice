from kafka import KafkaProducer
import json
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv(".env/development.env")

# Configuração do Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Função para enviar mensagens ao Kafka
def send_test_message():
    topic = 'invite-request'
    message = {
        "action": "upload_contract",
        "user_data": {
        "email": "tiagocgomes2003@gmail.com",
        "name": "teste",
        }
    }
    try:
        producer.send(topic, message)
        producer.flush()  # Garante que a mensagem seja enviada
        print(f"Mensagem enviada ao tópico '{topic}': {message}")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

if __name__ == "__main__":
    send_test_message()
