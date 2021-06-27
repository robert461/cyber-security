import os

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from security.hashing.generic_hash import GenericHash
from security.utils.hashing_utils import HashingUtils


class ScryptHash(GenericHash):

    # https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#scrypt

    def __init__(self):
        super().__init__()

        # defaults
        self.__hash_length = 32
        self.__cost_parameter = 2 ** 14
        self.__block_size = 8
        self.__parallelization = 1

        self.__salt_length = 16

    def get_key(self) -> bytes:

        salt = os.urandom(self.__salt_length)
        print(f'salt: {salt.hex()}')

        password_bytes = HashingUtils.get_password_from_user()

        key = self.__derive_key(password_bytes, salt)

        return key

    def get_key_with_existing_credentials(self) -> bytes:

        salt = HashingUtils.get_salt_from_user()

        password_bytes = HashingUtils.get_password_from_user()

        key = self.__derive_key(password_bytes, salt)

        return key

    def __derive_key(self, password_bytes: bytes, salt: bytes) -> bytes:
        kdf = Scrypt(
            salt = salt,
            length = self.__hash_length,
            n = self.__cost_parameter,
            r = self.__block_size,
            p = self.__parallelization,
        )

        key = kdf.derive(password_bytes)
        kdf.verify(password_bytes, key)

        return key
