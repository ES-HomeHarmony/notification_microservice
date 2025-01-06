import pytest
from unittest.mock import patch, mock_open
from app.main import process_tenant_paid

@pytest.fixture
def tenant_data():
    return {
        "email": "landlord@example.com",
        "name": "John Landlord",
        "tenant_name": "Jane Tenant",
        "expense_name": "Monthly Rent",
        "amount": 1200.0,
        "house_name": "Ocean View Apartments"
    }

@patch("builtins.open", new_callable=mock_open, read_data="""
    <html>
        <body>
            <p>Dear {{name}},</p>
            <p>Tenant {{tenant_name}} has paid {{expense_name}} of ${{amount}} for {{house_name}}.</p>
        </body>
    </html>
""")
@patch("app.main.send_email")
def test_process_tenant_paid_success(mock_send_email, mock_open, tenant_data):
    """Testa o sucesso do processamento do pagamento do inquilino."""
    # Chama a função
    process_tenant_paid(tenant_data)
    
    # Verifica se o template foi aberto corretamente
    mock_open.assert_called_once_with("templates/tenant_payment.html", 'r', encoding='utf-8')

    # Verifica se o send_email foi chamado com os argumentos esperados
    mock_send_email.assert_called_once_with(
        "landlord@example.com",
        "Tenant Payment Received!",
        """
    <html>
        <body>
            <p>Dear John Landlord,</p>
            <p>Tenant Jane Tenant has paid Monthly Rent of $1200.0 for Ocean View Apartments.</p>
        </body>
    </html>
"""
    )

def test_process_tenant_paid_missing_email(capfd, tenant_data):
    """Teste para verificar o comportamento quando o e-mail está ausente."""
    # Remove o campo 'email'
    del tenant_data["email"]

    # Executa a função e captura a saída
    process_tenant_paid(tenant_data)

    # Captura a saída padrão
    captured = capfd.readouterr()
    assert "Erro ao processar tenant_paid: Email do locador não encontrado." in captured.out


@patch("app.main.send_email")
def test_process_tenant_paid_send_email_error(mock_send_email, capfd, tenant_data):
    """Teste para verificar erro durante o envio de e-mail."""
    # Configura o mock para levantar uma exceção ao enviar o e-mail
    mock_send_email.side_effect = Exception("SMTP server error")

    # Executa a função e captura a saída
    process_tenant_paid(tenant_data)

    # Captura a saída padrão
    captured = capfd.readouterr()
    assert "Erro ao processar tenant_paid: SMTP server error" in captured.out
