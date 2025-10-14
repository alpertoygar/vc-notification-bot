from src.util import calculate_download_duration, is_str_with_reddit_url
import pytest


class TestCalculateDownloadDuration:
    def test_returns_duration_for_valid_input(self):
        assert calculate_download_duration("8", "8") == "137"
        assert calculate_download_duration("8", "0") == "0"

    def test_raises_exception_for_invalid_input(self):
        with pytest.raises(ValueError):
            calculate_download_duration("foo", "bar")

        with pytest.raises(ValueError):
            calculate_download_duration("1", "bar")

        with pytest.raises(ValueError):
            calculate_download_duration("foo", "2")

        with pytest.raises(ZeroDivisionError):
            calculate_download_duration("0", "1")


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
