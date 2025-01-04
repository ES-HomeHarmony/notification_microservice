from unittest import TestCase
from unittest.mock import patch, MagicMock, ANY
import os
from app.main import send_email

class TestSendEmail(TestCase):

    @patch.dict(os.environ, {
        "SMTP_HOST": "smtp.test.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "test_user@test.com",
        "SMTP_PASS": "test_password"
    })
    @patch("smtplib.SMTP")
    def test_send_email_success(self, mock_smtp):
        # Configura o mock do servidor SMTP
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Chama a função que será testada
        email_to = "recipient@test.com"
        subject = "Test Subject"
        html_message = "<p>This is a test email</p>"
        send_email(email_to, subject, html_message)

        # Verifica se os métodos corretos foram chamados
        mock_smtp.assert_called_once_with("smtp.test.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test_user@test.com", "test_password")
        mock_server.sendmail.assert_called_once_with(
            "test_user@test.com",
            email_to,
            ANY
        )
    @patch("smtplib.SMTP")
    def test_send_email_failure(self, mock_smtp):
        # Configura o mock para simular uma exceção
        mock_smtp.side_effect = Exception("SMTP error")

        # Verifica se a exceção ValueError é levantada
        with self.assertRaises(ValueError) as context:
            send_email("recipient@test.com", "Test Subject", "<p>This is a test email</p>")

        # Verifica se a mensagem da exceção contém o erro esperado
        self.assertIn("Erro ao enviar email: SMTP error", str(context.exception))
