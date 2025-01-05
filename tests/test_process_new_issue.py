import pytest
from unittest.mock import patch, mock_open
from app.main import process_new_issue

@pytest.fixture
def issue_data():
    return {
        "issue": {
            "title": "Leak in Kitchen",
            "description": "There is a water leak under the sink.",
            "status": "Open",
            "priority": "High"
        },
        "house_name": "Green Valley Apartments",
        "tenant_name": "John Doe",
        "users": [
            {"email": "user1@example.com", "name": "Manager 1"},
            {"email": "user2@example.com", "name": "Manager 2"}
        ]
    }

@patch("builtins.open", new_callable=mock_open, read_data="<h1>Dear, {{name}}</h1><p>Issue: {{title}}, Description: {{description}}, Status: {{status}}, Priority: {{priority}}</p>")
@patch("app.main.send_email")
def test_process_new_issue(mock_send_email, mock_open, issue_data):
    # Call the function
    process_new_issue(issue_data)
    
    # Assert the template was opened correctly
    mock_open.assert_called_once_with("templates/issue.html", 'r', encoding='utf-8')

    # Assert send_email was called for each user
    expected_calls = [
        ("user1@example.com", "New Issue Created!", "<h1>Dear, Manager 1</h1><p>Issue: Leak in Kitchen, Description: There is a water leak under the sink., Status: Open, Priority: High</p>"),
        ("user2@example.com", "New Issue Created!", "<h1>Dear, Manager 2</h1><p>Issue: Leak in Kitchen, Description: There is a water leak under the sink., Status: Open, Priority: High</p>")
    ]

    # Convert call_args_list to a list of tuples for comparison
    actual_calls = [call.args for call in mock_send_email.call_args_list]

    assert actual_calls == expected_calls

    # Ensure send_email was called the correct number of times
    assert mock_send_email.call_count == 2


def test_process_new_issue_missing_issue_details(capfd):
    """Teste para verificar a mensagem de erro quando issue está ausente."""
    issue_data = {
        "house_name": "Green Valley Apartments",
        "tenant_name": "John Doe",
        "users": [{"email": "user@example.com", "name": "Manager 1"}]
    }
    process_new_issue(issue_data)

    # Captura a saída padrão
    captured = capfd.readouterr()
    assert "Erro ao processar expense_created: Detalhes da issue não encontrados." in captured.out

def test_process_new_issue_missing_users(capfd):
    """Teste para verificar a mensagem de erro quando users está ausente."""
    issue_data = {
        "issue": {
            "title": "Leak in Kitchen",
            "description": "There is a water leak under the sink.",
            "status": "Open",
            "priority": "High"
        },
        "house_name": "Green Valley Apartments",
        "tenant_name": "John Doe"
    }
    process_new_issue(issue_data)

    # Captura a saída padrão
    captured = capfd.readouterr()
    assert "Erro ao processar expense_created: Nenhum usuário encontrado na mensagem." in captured.out

def test_process_new_issue_empty_users(capfd):
    """Teste para verificar a mensagem de erro quando a lista de usuários está vazia."""
    issue_data = {
        "issue": {
            "title": "Leak in Kitchen",
            "description": "There is a water leak under the sink.",
            "status": "Open",
            "priority": "High"
        },
        "house_name": "Green Valley Apartments",
        "tenant_name": "John Doe",
        "users": []
    }
    process_new_issue(issue_data)

    # Captura a saída padrão
    captured = capfd.readouterr()
    assert "Erro ao processar expense_created: Nenhum usuário encontrado na mensagem." in captured.out

@patch("app.main.send_email")
def test_process_new_issue_user_without_email(mock_send_email, capfd):
    """Testa comportamento ao processar usuários com e sem e-mail."""
    
    issue_data = {
        "issue": {
            "title": "Leak in Kitchen",
            "description": "There is a water leak under the sink.",
            "status": "Open",
            "priority": "High"
        },
        "house_name": "Green Valley Apartments",
        "tenant_name": "John Doe",
        "users": [
            {"name": "Manager Without Email"},  # Usuário sem e-mail
            {"email": "valid@example.com", "name": "Manager With Email"}  # Usuário válido
        ]
    }

    # Executa a função
    process_new_issue(issue_data)

    # Captura a saída padrão
    captured = capfd.readouterr()

    # Verifica mensagens no log
    assert "Usuário Manager Without Email não tem um e-mail válido, ignorando." in captured.out
    assert "E-mail enviado para valid@example.com" in captured.out

    # Verifica que o `send_email` foi chamado apenas uma vez (para o usuário válido)
    mock_send_email.assert_called_once()

    # Verifica os argumentos principais da chamada
    args, kwargs = mock_send_email.call_args
    assert args[0] == "valid@example.com"  # Verifica o e-mail do destinatário
    assert args[1] == "New Issue Created!"  # Verifica o assunto do e-mail
