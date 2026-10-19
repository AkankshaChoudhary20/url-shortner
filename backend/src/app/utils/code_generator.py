import secrets
import string

ALPHABET = string.ascii_letters + string.digits
DEFAULT_LENGTH = 7


def generate_short_code(length: int = DEFAULT_LENGTH) -> str:
    if type(length) is not int or length < 1:
        raise ValueError("length must be a positive integer")
    return "".join(secrets.choice(ALPHABET) for _ in range(length))

