from re import search, sub

TWITTER_POST_URL_REGEX = "(https:\/\/)(twitter|x)(\.com)(\/[^\/ ]+)(\/[^\/ ]+)(\/[^\/ ]+)"

def list_to_string(l: list):
    if not l:
        return ""  # Return an empty string if the input list is empty
    else:
        return ' '.join(map(str, l))

def is_str_with_twitter_url(str: str) -> bool:
    return search(TWITTER_POST_URL_REGEX, str) != None

def replace_twitter_url_in_match_object(match_object) -> str:
    match_groups = list(match_object.groups())
    match_groups[1] = "vxtwitter"
    return ''.join(match_groups)

def replace_twitter_urls_in_str(str: str) -> str:
    return sub(TWITTER_POST_URL_REGEX, replace_twitter_url_in_match_object, str)

