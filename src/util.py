from re import search, sub

TWITTER_POST_URL_REGEX = r"(https:\/\/)(twitter|x)(\.com)(\/[^\/ ]+)(\/[^\/ ]+)(\/[^\/ ]+)"


def list_to_string(input_list: list):
    if not input_list:
        return ""  # Return an empty string if the input list is empty
    else:
        return " ".join(map(str, input_list))


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
