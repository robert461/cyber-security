import os
from abc import abstractmethod
from typing import Optional

from security.hashing.generic_hash import GenericHash
from security.utils.hash_utils import HashUtils


class SaltedHash(GenericHash):
    """A class representing hashes which can be salted

    If initialized with said salt, it will use it for all operations. Otherwise, the salt
    will be generated randomly with os.urandom when encrypting. Or it will be asked from
    stdin when decrypting.
    """
    SALT_LENGTH = 16

    def __init__(self, is_test: Optional[bool] = False, salt: Optional[bytes] = None):
        super().__init__()

        self._is_test = is_test

        self._salt = salt
        if self._salt is None:
            self._salt = os.urandom(SaltedHash.SALT_LENGTH)

        assert len(self._salt) == SaltedHash.SALT_LENGTH, \
            f"Salt length unexpected {len(self._salt)} != {SaltedHash.SALT_LENGTH}!"

    @property
    def salt(self):
        return self._salt

    def get_key(self) -> bytes:

        password_bytes = HashUtils.get_password(self._is_test)

        key = self._derive_key(password_bytes)

        return key

    def get_key_with_existing_credentials(self) -> bytes:

        # if self._salt is None:
        #    self._salt = HashUtils.get_salt_from_user()

        password_bytes = HashUtils.get_password_from_user()

        key = self._derive_key(password_bytes)

        return key

    def _derive_key(self, password_bytes: bytes) -> bytes:
        kdf = self._get_kdf_instance()
        key = kdf.derive(password_bytes)

        kdf = self._get_kdf_instance()
        kdf.verify(password_bytes, key)

        return key

    @abstractmethod
    def _get_kdf_instance(self):
        """Returns key derivation function which differs for each hash function"""
        pass
