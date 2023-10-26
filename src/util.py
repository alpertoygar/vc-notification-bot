def list_to_string(l: list):
    if not l:
        return ""  # Return an empty string if the input list is empty
    else:
        return ' '.join(map(str, l))