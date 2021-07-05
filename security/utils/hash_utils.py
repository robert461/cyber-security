import random
import string
from getpass import getpass
from typing import Optional


class HashUtils:

    @staticmethod
    def get_password(is_test: Optional[bool] = False) -> bytes:
        if is_test:
            password_bytes = bytes(HashUtils.get_random_string(20), 'utf-8')
        else:
            password_bytes = HashUtils.get_password_from_user()

        return password_bytes

    @staticmethod
    def get_password_from_user() -> bytes:

        password = getpass('Please enter the password you want to use: ')

        password_bytes = bytes(password, 'utf-8')

        return password_bytes

    @staticmethod
    def get_salt_from_user() -> bytes:
        salt_string = input('Please enter the salt: ')

        salt = bytes.fromhex(salt_string)

        return salt

    @staticmethod
    def get_random_string(position_of_element: int) -> str:
        return ''.join(random.choices(string.ascii_letters, k=position_of_element))
