from reedsolo import RSCodec


# https://pypi.org/project/reedsolo/
class ReedSolomon:

    @staticmethod
    def encode(data: bytes, redundant_bits: int) -> bytes:

        if redundant_bits == 0:
            return data

        redundant_bytes = len(data) * redundant_bits // 8

        rsc = RSCodec(redundant_bytes)
        encoded_data = rsc.encode(data)

        return bytes(encoded_data)

    @staticmethod
    def decode(data: bytes, redundant_bits: int) -> bytes:

        if redundant_bits == 0:
            return data

        redundant_bytes = len(data) // (redundant_bits // 8 + 1)

        rsc = RSCodec(redundant_bytes)

        decoded_msg = rsc.decode(data)[0]

        return decoded_msg
