from typing import Optional
from encryption.generic_encryptor import GenericEncryptor


class NoneEncryptor(GenericEncryptor):

    # https://cryptography.io/en/latest/fernet/

    def __init__(self):
        super().__init__()

    def configure(self, force_use_existing_credentials: Optional[bool] = False):
        pass

    def encrypt(self, data: bytes) -> bytes:
        return data

    def decrypt(self, data: bytes) -> bytes:
        return data
