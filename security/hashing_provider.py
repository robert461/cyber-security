from security.enums.hashing_type import HashingType
from security.hashing.generic_hash import GenericHash
from security.hashing.none_hash import NoneHash
from security.hashing.pbkdf2_hash import Pbkdf2Hash
from security.hashing.scrypt_hash import ScryptHash


class HashingProvider:

    def __init__(self):
        pass

    @staticmethod
    def get_encryptor(hashing_type: HashingType) -> GenericHash:
        if not hashing_type or hashing_type == HashingType.NONE:
            return NoneHash()

        if hashing_type == HashingType.PBKDF2:
            return Pbkdf2Hash()

        if hashing_type == HashingType.SCRYPT:
            return ScryptHash()

        raise ValueError('Could not get Hash')
