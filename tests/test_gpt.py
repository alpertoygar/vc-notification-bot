import pytest
from unittest.mock import MagicMock, patch

from src.gpt import GPTClient


@pytest.fixture
def gpt_client_fixture():
    with patch("src.gpt.OpenAI") as openai:
        mock_openai = MagicMock()
        openai.return_value = mock_openai
        gpt_client = GPTClient()
        yield gpt_client, mock_openai


def test_ask_question(gpt_client_fixture):
    gpt_client, mock_openai = gpt_client_fixture

    mock_openai.chat = MagicMock(
        completions=MagicMock(
            create=MagicMock(return_value=MagicMock(choices=[MagicMock(message=MagicMock(content="Amsterdam"))]))
        )
    )

    content = "What is the capital of Netherlands?"
    response = gpt_client.ask_question(content)

    assert response == "Amsterdam"
    mock_openai.chat.completions.create.assert_called_once()
