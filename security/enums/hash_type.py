from enum import Enum


class HashType(Enum):

    NONE = 0
    PBKDF2 = 1
    SCRYPT = 2
