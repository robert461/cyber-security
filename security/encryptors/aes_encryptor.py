import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from security.encryption_utils import EncryptionUtils
from security.encryptors.generic_encryptor import GenericEncryptor


class AesEncryptor(GenericEncryptor):

    def __init__(self):
        super().__init__()

        self.__cipher: Cipher = None

    def configure(self, force_use_existing_credentials: Optional[bool] = False):

        if not force_use_existing_credentials:
            use_existing_credentials = EncryptionUtils.ask_user_if_existing_credentials_should_be_used()
        else:
            use_existing_credentials = True

        if use_existing_credentials:
            key = EncryptionUtils.get_key_from_user_input()
        else:
            key = os.urandom(32)

            print(f'key used: {key}')

        nonce = os.urandom(16)

        self.__cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))

    def encrypt(self, data: bytes) -> bytes:
        self.__check_if_configured()

        nonce = os.urandom(16)
        self.__cipher.mode = modes.CTR(nonce)

        encryptor = self.__cipher.encryptor()

        encrypted_data = encryptor.update(data) + encryptor.finalize()

        return encrypted_data

    def decrypt(self, data: bytes) -> bytes:
        self.__check_if_configured()

        decryptor = self.__cipher.decryptor()

        decrypted_data = decryptor.update(data) + decryptor.finalize()

        return decrypted_data

    def __check_if_configured(self):

        if not self.__cipher:
            raise RuntimeError('Encryptor not configured. Call configure() first.')
