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

    mock_openai.chat = MagicMock(
        completions=MagicMock(
            create=MagicMock(return_value=MagicMock(choices=[MagicMock(message=MagicMock(content="Amsterdam"))]))
        )
    )

    content = "What is the capital of Netherlands?"
    response = gpt_client.ask_question(content)

    assert response == "Amsterdam"
    mock_openai.chat.completions.create.assert_called_once_with(
        model=base_model,
        messages=pytest.approx(
            [
                {"role": "system", "content": "All answers must be shorter than 2000 characters."},
                {"role": "user", "content": content},
            ],
            abs=0,
        ),
    )


def test_ask_question_with_custom_model(gpt_client_fixture):
    gpt_client, mock_openai, _ = gpt_client_fixture

    mock_openai.chat = MagicMock(
        completions=MagicMock(
            create=MagicMock(return_value=MagicMock(choices=[MagicMock(message=MagicMock(content="Brussels"))]))
        )
    )

    content = "What is the capital of Belgium?"
    custom_model = "custom-model-name"
    response = gpt_client.ask_question(content, model=custom_model)

    assert response == "Brussels"
    mock_openai.chat.completions.create.assert_called_once_with(
        model=custom_model,
        messages=pytest.approx(
            [
                {"role": "system", "content": "All answers must be shorter than 2000 characters."},
                {"role": "user", "content": content},
            ],
            abs=0,
        ),
    )


def test_ask_when_taken(gpt_client_fixture):
    gpt_client, mock_openai, base_model = gpt_client_fixture

    mock_openai.chat = MagicMock(
        completions=MagicMock(
            create=MagicMock(
                return_value=MagicMock(choices=[MagicMock(message=MagicMock(content="Paris, France, 2010"))])
            )
        )
    )

    url = "http://example.com/image.jpg"
    response = gpt_client.ask_when_taken(url)

    assert response == "Paris, France, 2010"
    mock_openai.chat.completions.create.assert_called_once_with(
        model=base_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Tell me which city, country and year do you think this image taken? And what is your reasoning",
                    },
                    {"type": "image_url", "image_url": {"url": url}},
                ],
            }
        ],
    )
