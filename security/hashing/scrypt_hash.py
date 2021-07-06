from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from security.enums.hash_type import HashType
from security.hashing.salted_hash import SaltedHash


class ScryptHash(SaltedHash):

    # https://cryptography.io/en/latest/hazmat/primitives/key-derivation-functions/#scrypt
    HASH_TYPE = HashType.SCRYPT

    # defaults for this specific hash
    HASH_LENGTH = 32
    COST_PARAMETER = 2 ** 14
    BLOCK_SIZE = 8
    PARALLELIZATION = 1

    def _get_kdf_instance(self):
        kdf = Scrypt(
            salt=self._salt,
            length=ScryptHash.HASH_LENGTH,
            n=ScryptHash.COST_PARAMETER,
            r=ScryptHash.BLOCK_SIZE,
            p=ScryptHash.PARALLELIZATION,
        )
        return kdf
