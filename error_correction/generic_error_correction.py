from abc import ABC, abstractmethod


class GenericErrorCorrection(ABC):

    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def encode(data: bytes, redundant_bits: int) -> bytes:
        pass

    @staticmethod
    @abstractmethod
    def decode(data: bytes, redundant_bits: int) -> bytes:
        pass
