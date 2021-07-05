from reedsolo import RSCodec


class ReedSolomon:
    """Reed solomon wrapper for the reedsolo pip package

    redundant_bits show the number of bits to add for error correction for each byte. This has
    to be converted to the total number of redundant bytes for the entire message to be able to
    use the reedsolo package.

    https://pypi.org/project/reedsolo/
    """

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

        # E.g. if 4 bytes of data="test" encoded with redundant_bits=16, then data is 12 bytes long.
        # To get 8 total redundant bytes:
        #       divide 12 by (redundant_bytes+1) = (2+1) = 3, to get 4, this is the original message size in bytes
        #       now subtract this from the the encoded message length: 12 - 4 = 8
        redundant_bytes = redundant_bits // 8
        original_message_bytes = len(data) // (redundant_bytes + 1)
        redundant_bytes_total = len(data) - original_message_bytes

        rsc = RSCodec(redundant_bytes_total)

        decoded_msg = rsc.decode(data)[0]

        return decoded_msg
