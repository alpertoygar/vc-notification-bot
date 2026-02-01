from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def __init__(self, env_file: str | None = None, **kwargs):
        super().__init__(
            _env_file=env_file,
            **kwargs,
        )

    # Discord Bot Configuration
    bot_token: str = Field(..., description="Discord bot token")
    guild_id: int = Field(..., description="Discord guild ID")

    # GPT Configuration
    openai_key: str = Field(..., description="OpenAI API key")
    gpt_channel_id: int | None = Field(..., description="Channel ID for GPT commands")
    gpt_model_code: str | None = Field(..., description="GPT model for code generation")
    gpt_model_base: str | None = Field(..., description="GPT model for general conversation")
    gpt_query_token_limit: int | None = Field(..., description="Maximum tokens per GPT query")
    gpt_total_token_limit: int | None = Field(..., description="Maximum total tokens per hour for GPT")

    # Reddit Configuration
    reddit_client_id: str = Field(..., description="Reddit API client ID")
    reddit_client_secret: str = Field(..., description="Reddit API client secret")

    # BGG Configuration
    bgg_api_key: str | None = Field(None, description="BoardGameGeek API key")
