import base64
import os
from getpass import getpass
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from encryption.encryption_utils import EncryptionUtils
from encryption.generic_encryptor import GenericEncryptor


class FernetEncryptor(GenericEncryptor):

    # https://cryptography.io/en/latest/fernet/

    def __init__(self):
        super().__init__()

        self.__fernet: Fernet = None

    def configure(self, force_use_existing_credentials: Optional[bool] = False):

        if not force_use_existing_credentials:
            use_existing_credentials = EncryptionUtils.ask_user_if_existing_credentials_should_be_used()
        else:
            use_existing_credentials = True

        if use_existing_credentials:

            key = EncryptionUtils.get_base64_key_from_user_input()

            self.__fernet = Fernet(key)

        else:
            key = Fernet.generate_key()

            print(f'The password is: {key.decode("utf-8")}')

            self.__fernet = Fernet(key)

    def encrypt(self, data: bytes) -> bytes:
        self.__check_if_configured()

        encrypted_data = self.__fernet.encrypt(data)

        return encrypted_data

    def decrypt(self, data: bytes):
        self.__check_if_configured()

        decrypted_data = self.__fernet.decrypt(data)

        return decrypted_data

    def __check_if_configured(self):

        if not self.__fernet:
            raise RuntimeError('Encryptor not configured. Call configure() first.')
