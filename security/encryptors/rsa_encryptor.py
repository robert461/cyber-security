from typing import Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from security.encryptors.generic_encryptor import GenericEncryptor


class RsaEncryptor(GenericEncryptor):

    def __init__(self):
        super().__init__()

        self.__private_key = None
        self.__public_key = None

    def configure(self, force_use_existing_credentials: Optional[bool] = False):
        # TODO use case existing keys

        self.__private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048,)

        print(self.__private_key)

        self.__public_key = self.__private_key.public_key()

    def encrypt(self, data: bytes) -> bytes:
        self.__check_if_configured()

        encrypted_data = self.__public_key.encrypt(
            data,
            padding.OAEP(
                mgf = padding.MGF1(algorithm = hashes.SHA256()),
                algorithm = hashes.SHA256(),
                label = None
            )
        )

        return encrypted_data

    def decrypt(self, data: bytes) -> bytes:
        self.__check_if_configured()

        encrypted_data = self.__private_key.decrypt(
            data,
            padding.OAEP(
                mgf = padding.MGF1(hashes.SHA256()),
                algorithm = hashes.SHA256(),
                label = None
            )
        )

        return encrypted_data

    def __check_if_configured(self):

        if not self.__public_key or not self.__private_key:
            raise RuntimeError('Encryptor not configured. Call configure() first.')
