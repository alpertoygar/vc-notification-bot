from src.reddit import (
    RedditPostInfo,
    extract_reddit_post_content_from_str,
    fetch_reddit_post_info,
    format_reddit_post_info,
    is_str_with_reddit_url,
)
from unittest.mock import Mock, patch, AsyncMock
import pytest


class TestIsStrWithRedditUrl:
    @pytest.mark.parametrize(
        "test_str, expected",
        [
            ("https://www.reddit.com/r/MadeMeSmile/s/zLeQFI5Lk0", True),
            ("https://reddit.com/r/programming/comments/123abc/test_post/", True),
            ("https://www.reddit.com/r/Python/comments/xyz789/another_post/abc123", True),
            ("https://www.reddit.com/r/duneawakening/s/05Zj4wVwZj", True),
            ("Check this out: https://reddit.com/r/test/s/shortlink", True),
            ("Multiple: https://reddit.com/r/a/comments/1/title/ and text", True),
            ("https://twitter.com/user/status/123", False),
            ("https://github.com/user/repo", False),
            ("Just some text without URLs", False),
            ("https://example.com/reddit/fake", False),
            ("reddit.com without protocol", False),
        ],
    )
    def test_str_with_reddit_urls(self, test_str, expected):
        assert is_str_with_reddit_url(test_str) == expected


class TestFetchRedditPostInfo:
    mock_post_data = {
        "title": "Test Post",
        "selftext": "This is a test post",
        "author": "testuser",
        "subreddit": "testsub",
    }
    mock_json_response_value = [{"data": {"children": [{"data": mock_post_data}]}}]

    @pytest.mark.asyncio
    async def test_fetches_post_info_successfully(self):
        """Test that valid Reddit post URLs return correct post info."""
        with patch("src.reddit.RedditClient") as mock_client:
            # Mock the JSON response for the actual post
            mock_response = Mock()
            mock_response.json.return_value = self.mock_json_response_value
            mock_response.raise_for_status.return_value = None

            # Set up the mock RedditClient instance
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None

            mock_client.return_value = mock_client_instance

            result = await fetch_reddit_post_info("https://reddit.com/r/test/comments/123/test/")

            assert result is not None
            assert result.title == "Test Post"
            assert result.content == "This is a test post"
            assert result.author == "testuser"
            assert result.subreddit == "testsub"

            # Verify that get was called once with the JSON URL
            mock_client_instance.get.assert_called_once_with("https://reddit.com/r/test/comments/123/test.json")

    @pytest.mark.asyncio
    async def test_follows_redirects_for_shared_links(self):
        """Test that shared links (/s/) follow redirects correctly."""
        with patch("src.reddit.RedditClient") as mock_client:
            # Mock the redirect response for shared link
            mock_redirect_response = Mock()
            mock_redirect_response.url = "https://www.reddit.com/r/test/comments/abc123/test_post/"

            # Mock the JSON response for the actual post
            mock_json_response = Mock()
            mock_json_response.json.return_value = self.mock_json_response_value
            mock_json_response.raise_for_status.return_value = None

            # Set up the mock RedditClient instance to return different responses
            mock_client_instance = AsyncMock()
            mock_client_instance.get.side_effect = [mock_redirect_response, mock_json_response]
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None

            mock_client.return_value = mock_client_instance

            # Test with a shared link URL
            result = await fetch_reddit_post_info("https://reddit.com/r/test/s/abc123")

            # Verify the result
            assert result is not None
            assert result.title == "Test Post"
            assert result.content == "This is a test post"
            assert result.author == "testuser"
            assert result.subreddit == "testsub"

            # Verify that get was called twice (once for redirect, once for JSON)
            assert mock_client_instance.get.call_count == 2
            # First call should be the shared link
            assert mock_client_instance.get.call_args_list[0][0][0] == "https://reddit.com/r/test/s/abc123"
            # Second call should be the JSON URL
            assert (
                mock_client_instance.get.call_args_list[1][0][0]
                == "https://www.reddit.com/r/test/comments/abc123/test_post.json"
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "url, expected",
        [
            (
                "https://www.reddit.com/r/test/comments/abc123/test_post/?utm_source=share",
                "https://www.reddit.com/r/test/comments/abc123/test_post.json",
            ),
            (
                "https://www.reddit.com/r/test/comments/abc123/test_post?utm_source=share",
                "https://www.reddit.com/r/test/comments/abc123/test_post.json",
            ),
            (
                "https://www.reddit.com/r/test/comments/abc123/test_post/?utm_source=share&utm_medium=referral",
                "https://www.reddit.com/r/test/comments/abc123/test_post.json",
            ),
        ],
    )
    async def test_strips_query_parameters(self, url, expected):
        """Test that URLs with query parameters are handled correctly."""
        with patch("src.reddit.RedditClient") as mock_client:
            # Mock the JSON response for the actual post
            mock_response = Mock()
            mock_response.json.return_value = self.mock_json_response_value
            mock_response.raise_for_status.return_value = None

            # Set up the mock RedditClient instance
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None

            mock_client.return_value = mock_client_instance

            # Test with a URL that has query parameters
            await fetch_reddit_post_info(url)

            # Verify that get was called once for the JSON endpoint
            mock_client_instance.get.assert_called_once_with(expected)

    @pytest.mark.asyncio
    async def test_returns_none_for_empty_response(self):
        """Test that no data in the JSON response returns None."""
        with patch("src.reddit.RedditClient") as mock_client:
            # Mock an empty JSON response
            mock_response = Mock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None

            # Set up the mock RedditClient instance
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None

            mock_client.return_value = mock_client_instance

            result = await fetch_reddit_post_info("https://reddit.com/r/test/comments/123/test/")
            assert result is None


class TestFormatRedditPostInfo:
    @pytest.mark.parametrize(
        "post_info, expected",
        [
            (
                RedditPostInfo(
                    title="Test Post",
                    content="This is a test post",
                    author="testuser",
                    subreddit="testsub",
                ),
                "*Reddit Post from r/testsub by u/testuser*\n\n**Test Post**\n\nThis is a test post\n",
            ),
            (
                RedditPostInfo(
                    title="Test Post with URL",
                    content="https://example.com/image.jpg",
                    author="testuser",
                    subreddit="testsub",
                ),
                "*Reddit Post from r/testsub by u/testuser*\n\n**Test Post with URL**\n\n🔗 [Link to content](https://example.com/image.jpg)\n",
            ),
        ],
    )
    def test_formats_posts_successfully(self, post_info, expected):
        """Test formatting of Reddit post information."""
        result = format_reddit_post_info(post_info)
        assert result == expected

    def test_raises_exception_for_none_input(self):
        """Test that passing None raises a ValueError."""
        with pytest.raises(ValueError):
            format_reddit_post_info(None)


class TestExtractRedditPostContentFromStr:
    @pytest.mark.asyncio
    async def test_extracts_and_formats_post_successfully(self):
        """Test that valid Reddit post URLs return correctly formatted message."""
        mock_post_data: RedditPostInfo = {
            "title": "Test Post Title",
            "selftext": "This is some test content for the post.",
            "author": "testuser",
            "subreddit": "testsubreddit",
        }
        mock_json_response_value = [{"data": {"children": [{"data": mock_post_data}]}}]

        with patch("src.reddit.RedditClient") as mock_client:
            # Mock the JSON response for the actual post
            mock_response = Mock()
            mock_response.json.return_value = mock_json_response_value
            mock_response.raise_for_status.return_value = None

            # Set up the mock RedditClient instance
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None

            mock_client.return_value = mock_client_instance

            test_str = (
                "Check out this Reddit post: https://www.reddit.com/r/testsubreddit/comments/abc123/test_post_title/"
            )
            result = await extract_reddit_post_content_from_str(test_str)

            expected = "*Reddit Post from r/testsubreddit by u/testuser*\n\n**Test Post Title**\n\nThis is some test content for the post.\n"
            assert result == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "test_str",
        [
            "No Reddit URL here!",
            "Just some random text.",
            "Visit https://example.com for more info.",
        ],
    )
    async def test_raises_exception_for_str_without_reddit_url(self, test_str):
        """Test that passing a string without a Reddit URL raises a ValueError."""
        with pytest.raises(ValueError):
            await extract_reddit_post_content_from_str(test_str)
