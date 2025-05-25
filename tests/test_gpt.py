import pytest
from unittest.mock import MagicMock, patch

from src.gpt import GPTClient


@pytest.fixture
def gpt_client_fixture():
    with patch("src.gpt.OpenAI") as openai:
        mock_openai = MagicMock()
        openai.return_value = mock_openai
        base_model = "gpt-4.1-mini"
        gpt_client = GPTClient(base_model)
        yield gpt_client, mock_openai, base_model


def test_ask_question(gpt_client_fixture):
    gpt_client, mock_openai, base_model = gpt_client_fixture

    mock_openai.responses.create.return_value = MagicMock(
        id="response_123",
        output=[MagicMock(type="message", content=[MagicMock(text="Amsterdam")])],
        usage=MagicMock(total_tokens=42),
    )

    content = "What is the capital of Netherlands?"
    response = gpt_client.ask_question(content, "")

    assert response == ("Amsterdam", 42)
    mock_openai.responses.create.assert_called_once_with(model=base_model, input=content, previous_response_id=None)
