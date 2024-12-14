import re

from core.const import PWD_SPECIAL_CHARS


def check_username(username: str) -> bool:
    if not (username.isalnum() and username.isascii()):
        return False
    return True


def check_email(email: str) -> bool:
    email_pattern = re.compile(r"^\S+@\S+\.([a-z]{2,})+$")
    if not re.fullmatch(email_pattern, email):
        return False
    return True


def check_strong_pwd(password: str) -> bool:
    lower_count, upper_count, special_char_count, digit_count = 0, 0, 0, 0
    if len(password) >= 8:
        for char in password:
            lower_count += int(char.islower())
            upper_count += int(char.isupper())
            digit_count += int(char.isdigit())
            special_char_count += int(char in PWD_SPECIAL_CHARS)

    checks = [lower_count, upper_count, digit_count, special_char_count]
    if not all(checks):
        return False
    return True
