import re


def username_check(value):
    """Проверка username"""
    regex = r"^[a-zA-Z]+[a-zA-Z0-9_-]*"
    username_regex = re.fullmatch(regex, value)
    if len(value) < 2 or not username_regex:
        return False
    return True
