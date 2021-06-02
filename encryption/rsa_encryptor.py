from typing import Optional

from encryption.generic_encryptor import GenericEncryptor


class RsaEncryptor(GenericEncryptor):

    def __init__(self):
        super().__init__()

    def configure(self, force_use_existing_credentials: Optional[bool] = False):
        raise NotImplementedError

    def encrypt(self, data: bytes) -> bytes:
        raise NotImplementedError

    def decrypt(self, data: bytes):
        raise NotImplementedError
