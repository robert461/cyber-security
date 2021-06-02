import base64
import os
from getpass import getpass

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from encryption.generic_encryptor import GenericEncryptor


class FernetEncryptor(GenericEncryptor):

    def __init__(self):
        super().__init__()

        self.__fernet: Fernet = None

    def configure(self):

        use_existing_credentials = self.ask_user_if_existing_credentials_should_be_used()

        if use_existing_credentials:

            password = getpass('Please enter the password you want to use: ')

            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm = hashes.SHA256(),
                length = 32,
                salt = salt,
                iterations = 100000,
            )

            password_bytes = bytes(password, 'utf-8')

            key = base64.urlsafe_b64encode(kdf.derive(password_bytes))

            self.__fernet = Fernet(key)

        else:
            key = Fernet.generate_key()

            print(f'The password is: {key.decode("utf-8")}')

            self.__fernet = Fernet(key)

    def encrypt(self, data: bytes) -> bytes:
        encrypted_data = self.__fernet.encrypt(data)

        return encrypted_data

    def decrypt(self, data: bytes):
        decrypted_data = self.__fernet.decrypt(data)

        return decrypted_data
