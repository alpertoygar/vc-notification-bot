from src.util import calculate_download_duration
import pytest


def test_calculate_download_duration():
    assert calculate_download_duration("8", "8") == "137"
    assert calculate_download_duration("8", "0") == "0"


def test_calculate_download_duration_raises_exception_if_invalid_input():
    with pytest.raises(ValueError):
        calculate_download_duration("foo", "bar")

    with pytest.raises(ValueError):
        calculate_download_duration("1", "bar")

    with pytest.raises(ValueError):
        calculate_download_duration("foo", "2")

    with pytest.raises(ZeroDivisionError):
        calculate_download_duration("0", "1")
