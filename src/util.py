from re import search, sub
import httpx
from typing import Optional, Dict, Any, TypedDict


class RedditPostInfo(TypedDict):
    title: str
    content: str
    author: str
    subreddit: str


REDDIT_POST_URL_REGEX = r"https:\/\/(?:www\.)?reddit\.com\/r\/[a-zA-Z0-9_]+(?:\/[^\s]*)?(?=\s|$|[^\w\/])"
TWITTER_POST_URL_REGEX = r"(https:\/\/)(twitter|x)(\.com)(\/[^\/ ]+)(\/[^\/ ]+)(\/[^\/ ]+)"


def list_to_string(input_list: list):
    if not input_list:
        return ""  # Return an empty string if the input list is empty
    else:
        return " ".join(map(str, input_list))


def is_str_with_reddit_url(str: str) -> bool:
    return search(REDDIT_POST_URL_REGEX, str) is not None


def is_str_with_twitter_url(str: str) -> bool:
    return search(TWITTER_POST_URL_REGEX, str) is not None


def replace_twitter_url_in_match_object(match_object) -> str:
    match_groups = list(match_object.groups())
    match_groups[1] = "vxtwitter"
    return "".join(match_groups)


def replace_twitter_urls_in_str(str: str) -> str:
    return sub(TWITTER_POST_URL_REGEX, replace_twitter_url_in_match_object, str)


def calculate_download_duration(speed_in_mbit: str, size_in_gb: str) -> str:
    speed = float(speed_in_mbit) / 8
    size = float(size_in_gb) * 1024
    seconds = size / speed
    minutes = "{0:.3g}".format(seconds / 60)
    return minutes


async def fetch_reddit_post_info(url: str) -> Optional[RedditPostInfo]:
    """
    Fetches Reddit post information from a Reddit URL.
    Returns a dictionary with title, content, author, and subreddit information.
    """
    try:
        # Standard headers for all requests
        headers = {"User-Agent": "vc-notification-bot"}

        # Handle shared links (/s/) by following redirects to get the actual post URL
        if "/s/" in url:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                url = str(response.url)

        # Remove query parameters and add .json suffix
        clean_url = url.split("?")[0]
        json_url = clean_url.rstrip("/") + ".json"

        # Fetch post data from Reddit's JSON API
        async with httpx.AsyncClient() as client:
            response = await client.get(json_url, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            # Extract post data from Reddit API response structure
            if isinstance(data, list) and len(data) > 0:
                post_data = data[0]["data"]["children"][0]["data"]

                return {
                    "title": post_data.get("title", "No title"),
                    "content": post_data.get("selftext", "") or post_data.get("url", ""),
                    "author": post_data.get("author", "Unknown"),
                    "subreddit": post_data.get("subreddit", "Unknown"),
                }
            else:
                return None

    except Exception as e:
        print(f"Error fetching Reddit post: {e}")
        return None


def format_reddit_post_info(post_info: RedditPostInfo) -> str:
    """
    Formats Reddit post information into a Discord-friendly message.
    """
    if not post_info:
        raise ValueError("post_info cannot be None")

    title = post_info["title"]
    content = post_info["content"]
    author = post_info["author"]
    subreddit = post_info["subreddit"]

    # Truncate content if it's too long for Discord
    max_content_length = 1200  # Leave room for embeds and other content
    if content and len(content) > max_content_length:
        content = content[:max_content_length] + "..."

    # Format the message with better Discord formatting
    message = f"*Reddit Post from r/{subreddit} by u/{author}*\n\n"
    message += f"**{title}**\n"

    if content and content.strip() and not content.startswith("http"):
        # Only show content if it's text, not just a URL
        message += f"\n{content}\n"
    elif content and content.startswith("http"):
        # If content is a URL (like an image), mention it
        message += f"\n🔗 [Link to content]({content})\n"

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
