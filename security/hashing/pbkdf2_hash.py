from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from security.enums.hash_type import HashType
from security.hashing.salted_hash import SaltedHash


class Pbkdf2Hash(SaltedHash):

    # https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#pbkdf2
    HASH_TYPE = HashType.PBKDF2

    # defaults specific for pbkdf
    HASH_LENGTH = 32
    HASH_ITERATIONS = 100000

    def _get_kdf_instance(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=Pbkdf2Hash.HASH_LENGTH,
            salt=self._salt,
            iterations=Pbkdf2Hash.HASH_ITERATIONS,
        )

        return kdf
