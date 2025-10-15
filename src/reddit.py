import os
from re import search
import httpx
from typing import Optional

from pydantic import BaseModel
import requests

REDDIT_POST_URL_REGEX = r"https:\/\/(?:www\.)?reddit\.com\/r\/[a-zA-Z0-9_]+(?:\/[^\s]*)?(?=\s|$|[^\w\/])"


class RedditPostInfo(BaseModel):
    title: str
    content: str
    author: str
    subreddit: str


class RedditClient:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedditClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
            reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")

            auth = requests.auth.HTTPBasicAuth(reddit_client_id, reddit_client_secret)
            self.headers = {"User-Agent": "vc-notification-bot"}
            data = {"grant_type": "client_credentials"}
            res = requests.post(
                "https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=self.headers
            )
            TOKEN = res.json()["access_token"]

            self.headers = {**self.headers, **{"Authorization": f"bearer {TOKEN}"}}
            self.client = httpx.AsyncClient(follow_redirects=True, headers=self.headers, timeout=10.0)
            RedditClient._initialized = True

    async def get(self, url: str) -> httpx.Response:
        # replace www with oauth
        url = url.replace("www.", "")
        url = url.replace("reddit.com", "oauth.reddit.com")

        return await self.client.get(url)

    @classmethod
    async def close(cls):
        """Close the HTTP client when done."""
        if hasattr(cls._instance, "client"):
            await cls._instance.client.aclose()
        cls._instance = None
        cls._initialized = False


def is_str_with_reddit_url(str: str) -> bool:
    return search(REDDIT_POST_URL_REGEX, str) is not None


async def fetch_reddit_post_info(url: str) -> Optional[RedditPostInfo]:
    """
    Fetches Reddit post information from a Reddit URL.
    Returns a dictionary with title, content, author, and subreddit information.
    """
    reddit_client = RedditClient()

    # Handle shared links (/s/) by following redirects to get the actual post URL
    if "/s/" in url:
        response = await reddit_client.get(url)
        url = str(response.url)

    # Remove query parameters and add .json suffix
    clean_url = url.split("?")[0]
    json_url = clean_url.rstrip("/") + ".json"

    # Fetch post data from Reddit's JSON API
    response = await reddit_client.get(json_url)
    response.raise_for_status()
    data = response.json()

    # Extract post data from Reddit API response structure
    if data:
        post_data = data[0]["data"]["children"][0]["data"]

        return RedditPostInfo(
            title=post_data.get("title", "No title"),
            content=post_data.get("selftext", "") or post_data.get("url", ""),
            author=post_data.get("author", "Unknown"),
            subreddit=post_data.get("subreddit", "Unknown"),
        )
    else:
        return None


def format_reddit_post_info(post_info: RedditPostInfo) -> str:
    """
    Formats Reddit post information into a Discord-friendly message.
    """
    if not post_info:
        raise ValueError("post_info cannot be None")

    title = post_info.title
    content = post_info.content.strip()
    author = post_info.author
    subreddit = post_info.subreddit

    # Truncate content if it's too long for Discord
    max_content_length = 1200  # Leave room for embeds and other content
    if content and len(content) > max_content_length:
        content = content[:max_content_length] + "..."

    # Format the message with better Discord formatting
    message = f"*Reddit Post from r/{subreddit} by u/{author}*\n\n"
    message += f"**{title}**\n"

    if content.startswith("http"):
        # If content is a URL (like an image), mention it
        message += f"\n🔗 [Link to content]({content})\n"
    else:
        # Only show content if it's text, not just a URL
        message += f"\n{content}\n"

    return message


async def extract_reddit_post_content_from_str(str: str) -> str:
    """
    Extracts and returns the content from Reddit post information.
    """
    match = search(REDDIT_POST_URL_REGEX, str)
    if match:
        post_url = match.group(0)
        post_info = await fetch_reddit_post_info(post_url)
        formatted_message = format_reddit_post_info(post_info)
        return formatted_message

    raise ValueError("No Reddit URL found in the provided string")
