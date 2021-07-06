from reedsolo import RSCodec

from error_correction.generic_error_correction import GenericErrorCorrection


class ReedSolomonErrorCorrection(GenericErrorCorrection):
    """Reed solomon wrapper for the reedsolo pip package

    redundant_bits show the number of bits to add for error correction for each byte. This has
    to be converted to the total number of redundant bytes for the entire message to be able to
    use the reedsolo package.

    https://pypi.org/project/reedsolo/
    """

    @staticmethod
    def _get_ecc_byte_count_per_chunk(redundant_bits):
        redundant_bytes = redundant_bits // 8
        reed_solomon_chunk_size = 255
        if not (1 <= redundant_bytes < reed_solomon_chunk_size):
            raise ValueError(f"Too many redundant bytes: {redundant_bytes} must be less than {reed_solomon_chunk_size}!"
                             f"I.e. redundant_bits={redundant_bits} must be less than {reed_solomon_chunk_size * 8}!")
        data_bytes = reed_solomon_chunk_size // (redundant_bytes + 1)
        return reed_solomon_chunk_size - data_bytes

    @staticmethod
    def encode(data: bytes, redundant_bits: int) -> bytes:

        if redundant_bits == 0:
            return data

        ecc_byte_count_per_chunk = ReedSolomonErrorCorrection._get_ecc_byte_count_per_chunk(redundant_bits)

        rsc = RSCodec(ecc_byte_count_per_chunk)
        encoded_data = rsc.encode(data)

        return bytes(encoded_data)

    @staticmethod
    def decode(data: bytes, redundant_bits: int) -> bytes:

        if redundant_bits == 0:
            return data

        ecc_byte_count_per_chunk = ReedSolomonErrorCorrection._get_ecc_byte_count_per_chunk(redundant_bits)

        rsc = RSCodec(ecc_byte_count_per_chunk)

        decoded_msg = rsc.decode(data)[0]

        # important to return bytes, as rsc returns a bytearray, which causes errors in various encryptors
        return bytes(decoded_msg)
