import tempfile
import pytest
from pydantic import ValidationError

from src.settings import Settings

from contextlib import contextmanager

# Default environment content for the test environment file
DEFAULT_ENV_CONTENT = """
BOT_TOKEN=test_token
GUILD_ID=123456789
OPENAI_KEY=test_openai_key
GPT_CHANNEL_ID=987654321
GPT_MODEL_CODE=gpt-4
GPT_MODEL_BASE=gpt-3.5-turbo
GPT_QUERY_TOKEN_LIMIT=1000
GPT_TOTAL_TOKEN_LIMIT=10000
REDDIT_CLIENT_ID=test_reddit_id
REDDIT_CLIENT_SECRET=test_reddit_secret
"""


@pytest.fixture
def temp_env_file_with_content():
    """Fixture factory that creates a temp file with custom content."""

    @contextmanager
    def _create_file(content: str = DEFAULT_ENV_CONTENT) -> str:
        with tempfile.NamedTemporaryFile(mode="w+t", suffix=".env", delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_file.seek(0)
            yield tmp_file.name

    return _create_file


class TestSettings:
    """Tests for the Settings class."""

    def test_required_fields_missing(self):
        """Test that ValidationError is raised when required fields are missing."""
        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        error_fields = {error["loc"][0] for error in errors}

        # Check that all required fields are in the error
        required_fields = {"bot_token", "guild_id", "openai_key", "reddit_client_id", "reddit_client_secret"}
        assert required_fields.issubset(error_fields)

    def test_all_required_fields_provided(self, temp_env_file_with_content):
        """Test that all required fields are provided."""
        with temp_env_file_with_content() as temp_env_file:
            settings = Settings(env_file=temp_env_file)

        assert settings.bot_token == "test_token"
        assert settings.guild_id == 123456789
        assert settings.openai_key == "test_openai_key"
        assert settings.reddit_client_id == "test_reddit_id"
        assert settings.reddit_client_secret == "test_reddit_secret"
        assert settings.gpt_channel_id == 987654321
        assert settings.gpt_model_code == "gpt-4"
        assert settings.gpt_model_base == "gpt-3.5-turbo"
        assert settings.gpt_query_token_limit == 1000
        assert settings.gpt_total_token_limit == 10000

    def test_optional_fields_default_to_none(self, temp_env_file_with_content):
        """Test that optional fields default to None when not provided."""
        with temp_env_file_with_content() as temp_env_file:
            settings = Settings(env_file=temp_env_file)

        assert settings.bgg_api_key is None

    def test_optional_fields_can_be_set(self, temp_env_file_with_content):
        """Test that optional fields can be set with values."""
        with temp_env_file_with_content(
            DEFAULT_ENV_CONTENT
            + """
BGG_API_KEY=test_bgg_api_key
"""
        ) as temp_env_file:
            settings = Settings(env_file=temp_env_file)

        assert settings.bgg_api_key == "test_bgg_api_key"

    def test_guild_id_type_validation(self, temp_env_file_with_content):
        """Test that guild_id must be an integer."""
        with temp_env_file_with_content(
            DEFAULT_ENV_CONTENT
            + """
GUILD_ID=not_an_int
"""
        ) as temp_env_file:
            with pytest.raises(ValidationError) as exc_info:
                Settings(env_file=temp_env_file)

            errors = exc_info.value.errors()
            assert any(error["loc"][0] == "guild_id" for error in errors)

    def test_guild_id_accepts_integer_string(self, temp_env_file_with_content):
        """Test that guild_id can be provided as a string that can be converted to int."""
        with temp_env_file_with_content(
            DEFAULT_ENV_CONTENT
            + """
GUILD_ID="123456789"
"""
        ) as temp_env_file:
            settings = Settings(
                env_file=temp_env_file,
            )

        assert isinstance(settings.guild_id, int)
        assert settings.guild_id == 123456789

    def test_extra_fields_ignored(self, temp_env_file_with_content):
        """Test that extra fields are ignored (extra='ignore' setting)."""
        with temp_env_file_with_content(
            DEFAULT_ENV_CONTENT
            + """
extra_field=should_be_ignored
"""
        ) as temp_env_file:
            settings = Settings(
                env_file=temp_env_file,
            )

        # Should not raise an error and should not have extra_field
        assert not hasattr(settings, "extra_field")

    def test_loads_from_environment_variables(self, monkeypatch):
        """Test that Settings loads from environment variables."""
        monkeypatch.setenv("BOT_TOKEN", "env_bot_token")
        monkeypatch.setenv("GUILD_ID", "999888777")
        monkeypatch.setenv("OPENAI_KEY", "env_openai_key")
        monkeypatch.setenv("REDDIT_CLIENT_ID", "env_reddit_id")
        monkeypatch.setenv("REDDIT_CLIENT_SECRET", "env_reddit_secret")
        monkeypatch.setenv("GPT_CHANNEL_ID", "111222333")
        monkeypatch.setenv("GPT_MODEL_CODE", "gpt-4-turbo")
        monkeypatch.setenv("GPT_MODEL_BASE", "gpt-3.5-turbo")
        monkeypatch.setenv("GPT_QUERY_TOKEN_LIMIT", "2000")
        monkeypatch.setenv("GPT_TOTAL_TOKEN_LIMIT", "20000")
        monkeypatch.setenv("BGG_API_KEY", "env_bgg_api_key")

        settings = Settings()

        assert settings.bot_token == "env_bot_token"
        assert settings.guild_id == 999888777
        assert settings.openai_key == "env_openai_key"
        assert settings.reddit_client_id == "env_reddit_id"
        assert settings.reddit_client_secret == "env_reddit_secret"
        assert settings.gpt_channel_id == 111222333
        assert settings.gpt_model_code == "gpt-4-turbo"
        assert settings.gpt_model_base == "gpt-3.5-turbo"
        assert settings.gpt_query_token_limit == 2000
        assert settings.gpt_total_token_limit == 20000
        assert settings.bgg_api_key == "env_bgg_api_key"
