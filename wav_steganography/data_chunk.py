from dataclasses import dataclass


@dataclass
class DataChunk:
    data: bytes
    least_significant_bits: int
    every_nth_byte: int