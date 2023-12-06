import hashlib
import os
import secrets
import datetime
import random
import string

salt_file = os.environ["SALT_FILE"]
with open(salt_file, 'r') as file:
    salt = file.read()


def hash_password(password: str) -> bytes:
    password_with_salt = salt + password
    hash_ = hashlib.sha256(password_with_salt.encode("utf-8"), usedforsecurity=True)
    hashed_password = hash_.digest()
    return hashed_password


def generate_token() -> str:
    token = secrets.token_urlsafe(32)
    return token


def get_expiration_date(expiration_in_minutes: int = 1_440) -> datetime.datetime:
    return datetime.datetime.now() + datetime.timedelta(minutes=expiration_in_minutes)


def verify_password(password: str, hashed_password: str) -> bool:
    to_check = hash_password(password)
    return secrets.compare_digest(hashed_password, to_check)


def create_and_hash_random_password() -> (str, bytes):
    characters = string.printable
    password = ''.join(secrets.choice(characters) for _ in range(34))

    big_letters = string.ascii_uppercase
    random_value = random.randint(0, 25)
    password += big_letters[random_value]

    digits = string.digits
    random_value = random.randint(0, 9)
    password += digits[random_value]

    password_hash = hash_password(password)
    return password, password_hash
