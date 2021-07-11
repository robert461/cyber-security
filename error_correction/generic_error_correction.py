from abc import ABC, abstractmethod

from error_correction.error_correction_type import ErrorCorrectionType


class GenericErrorCorrection(ABC):

    def __init__(self, error_correction_type: ErrorCorrectionType):
        self.error_correction_type: ErrorCorrectionType = error_correction_type

    @staticmethod
    @abstractmethod
    def encode(data: bytes, redundant_bits: int) -> bytes:
        pass

    @staticmethod
    @abstractmethod
    def decode(data: bytes, redundant_bits: int) -> bytes:
        pass
