import base64
import os
from getpass import getpass

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from security.hashing.salted_hash import SaltedHash


class EncryptionUtils:

    @staticmethod
    def ask_user_if_existing_credentials_should_be_used():

        user_input = input('Do you want to enter existing credentials? (yes/no): ')

        if user_input == 'yes':
            return True
        if user_input == 'no':
            return False

    @staticmethod
    def get_key_from_user_input() -> bytes:

        password = getpass('Please enter the password you want to use: ')

        salt = os.urandom(SaltedHash.SALT_LENGTH)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        password_bytes = bytes(password, 'utf-8')

        key = kdf.derive(password_bytes)

        return key

    @staticmethod
    def get_base64_key_from_user_input() -> bytes:

        key = EncryptionUtils.get_key_from_user_input()

        base64_key = base64.urlsafe_b64encode(key)

        return base64_key
