from reedsolo import RSCodec


# https://pypi.org/project/reedsolo/
class ReedSolomon:

    @staticmethod
    def encode(data: bytes) -> bytes:

        rsc = RSCodec(10)  # 10 ecc symbols

        encoded_data = rsc.encode(data)

        print("Encoded with Reed Solomon")

        return encoded_data

    @staticmethod
    def decode(data: bytes) -> bytes:

        rsc = RSCodec(10)  # 10 ecc symbols

        decoded_msg, decoded_msgecc, errata_pos = rsc.decode(data)

        print("Decoded with Reed Solomon")

        return decoded_msg
