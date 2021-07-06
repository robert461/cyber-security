from dataclasses import dataclass


@dataclass
class DataChunk:
    data: bytes
    least_significant_bits: int
    every_nth_byte: int

    @property
    def amplitudes_required(self):
        """e.g. saving b'AB' requires 16 bits, with lsb=2 this means it can be encoded within 8 amplitudes"""
        return len(self.data) * 8 * self.every_nth_byte // self.least_significant_bits