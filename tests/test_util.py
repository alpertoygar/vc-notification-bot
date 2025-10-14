from src.util import calculate_download_duration
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
