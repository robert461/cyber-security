from enum import Enum


class HashingType(Enum):

    NONE = 0
    PBKDF2 = 1
    SCRYPT = 2
