import pytest
from unittest.mock import patch, mock_open
from app.main import process_expense_created

@pytest.fixture
def expense_data():
    return {
        "expense_details": {
            "title": "Água",
            "amount": 12,
            "deadline_date": "2025-01-15"
        },
        "users": [
            {"email": "user1@example.com", "name": "Usuário 1"},
            {"email": "user2@example.com", "name": "Usuário 2"}
        ]
    }

@patch("builtins.open", new_callable=mock_open, read_data="<h1>Dear, {{name}}</h1><p>Expense: {{title}}, Amount: {{amount}}, Due: {{deadline_date}}</p>")
@patch("app.main.send_email")
def test_process_expense_created(mock_send_email, mock_open, expense_data):
    # Call the function
    process_expense_created(expense_data)
    
    # Assert the template was opened correctly
    mock_open.assert_called_once_with("templates/expense.html", 'r', encoding='utf-8')

    # Assert send_email was called for each user
    expected_calls = [
        ("user1@example.com", "Expense Created!", "<h1>Dear, Usuário 1</h1><p>Expense: Água, Amount: 12, Due: 2025-01-15</p>"),
        ("user2@example.com", "Expense Created!", "<h1>Dear, Usuário 2</h1><p>Expense: Água, Amount: 12, Due: 2025-01-15</p>")
    ]

    # Convert call_args_list to a list of tuples for comparison
    actual_calls = [call.args for call in mock_send_email.call_args_list]

    assert actual_calls == expected_calls

    # Ensure send_email was called the correct number of times
    assert mock_send_email.call_count == 2


def test_process_expense_created_missing_expense_details(capfd):
    """Teste para verificar a mensagem de erro quando expense_details está ausente."""
    expense_data = {"users": [{"email": "user@example.com", "name": "Usuário"}]}
    process_expense_created(expense_data)

    # Captura a saída padrão
    captured = capfd.readouterr()
    assert "Erro ao processar expense_created: Detalhes da despesa não encontrados." in captured.out

def test_process_expense_created_missing_users(capfd):
    """Teste para verificar a mensagem de erro quando users está ausente."""
    expense_data = {"expense_details": {"title": "Água", "amount": 12}}
    process_expense_created(expense_data)

    # Captura a saída padrão
    captured = capfd.readouterr()
    assert "Erro ao processar expense_created: Nenhum usuário encontrado na mensagem." in captured.out

def test_process_expense_created_empty_users(capfd):
    """Teste para verificar a mensagem de erro quando a lista de usuários está vazia."""
    expense_data = {
        "expense_details": {"title": "Água", "amount": 12},
        "users": []
    }
    process_expense_created(expense_data)

    # Captura a saída padrão
    captured = capfd.readouterr()
    assert "Erro ao processar expense_created: Nenhum usuário encontrado na mensagem." in captured.out

@patch("app.main.send_email")
def test_process_expense_created_user_without_email(mock_send_email, capfd):
    """Testa comportamento ao processar usuários com e sem e-mail."""
    
    expense_data = {
        "expense_details": {"title": "Energia", "amount": 50, "deadline_date": "2025-02-01"},
        "users": [
            {"name": "Usuário Sem Email"},  # Usuário sem e-mail
            {"email": "valid@example.com", "name": "Usuário Válido"}  # Usuário válido
        ]
    }

    # Executa a função
    process_expense_created(expense_data)

    # Captura a saída padrão
    captured = capfd.readouterr()

    # Verifica mensagens no log
    assert "Usuário Usuário Sem Email não tem um e-mail válido, ignorando." in captured.out
    assert "E-mail enviado para valid@example.com" in captured.out

    # Verifica que o `send_email` foi chamado apenas uma vez (para o usuário válido)
    mock_send_email.assert_called_once()

    # Verifica os argumentos principais da chamada
    args, kwargs = mock_send_email.call_args
    assert args[0] == "valid@example.com"  # Verifica o e-mail do destinatário
    assert args[1] == "Expense Created!"  # Verifica o assunto do e-mail