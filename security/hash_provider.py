from security.enums.hash_type import HashType
from security.hashing.generic_hash import GenericHash
from security.hashing.none_hash import NoneHash
from security.hashing.pbkdf2_hash import Pbkdf2Hash
from security.hashing.scrypt_hash import ScryptHash


class HashProvider:

    def __init__(self):
        pass

    @staticmethod
    def get_hash(hash_type: HashType) -> GenericHash:
        if not hash_type or hash_type == HashType.NONE:
            return NoneHash()

        if hash_type == HashType.PBKDF2:
            return Pbkdf2Hash()

        if hash_type == HashType.SCRYPT:
            return ScryptHash()

        raise ValueError('Could not get Hash')
