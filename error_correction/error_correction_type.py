from enum import Enum


class ErrorCorrectionType(Enum):

    NONE = 0
    HAMMING = 1
    REED_SOLOMON = 2
