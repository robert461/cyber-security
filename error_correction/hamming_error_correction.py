import numpy as np


class HammingErrorCorrection:

    @staticmethod
    def encode_hamming_error_correction(data: bytes, redundant_bits: int) -> bytes:

        data_list = list(data)
        data_list.reverse()

        data_as_bits, hamming_code = [], []

        while len(data_list) > 0:
            data_as_bits = HammingErrorCorrection.convert_bytes_to_bits(data_list)

            number_of_data_and_redundant_bits = len(data_as_bits) + redundant_bits

            hamming_code_with_placeholders = \
                HammingErrorCorrection.add_placeholder_redundant_bits(data_as_bits, number_of_data_and_redundant_bits)

            hamming_code_calculated = \
                HammingErrorCorrection.calculate_values_for_redundant_bits(redundant_bits,
                                                                           number_of_data_and_redundant_bits,
                                                                           hamming_code_with_placeholders)

            hamming_code.extend(hamming_code_calculated)

            data_list.pop()

        hamming_code_byte = HammingErrorCorrection.convert_bits_to_bytes(hamming_code)

        hamming_code_byte_string = b''.join(hamming_code_byte)

        return hamming_code_byte_string

    @staticmethod
    def decode_hamming_error_correction(data: bytes, redundant_bits: int) -> bytes:

        data_list = list(data)

        decoded_hamming_code, data_as_bits = [], []

        for value in data_list:
            data_as_bits.extend([int(i) for i in str(np.binary_repr(value, 8))])

        number_of_data_and_redundant_bits = 8 + redundant_bits

        while len(data_as_bits) > 0:
            next_hamming_bits = data_as_bits[:number_of_data_and_redundant_bits]

            cleaned_hamming_bits = HammingErrorCorrection.remove_all_redundant_bits(next_hamming_bits, redundant_bits)

            decoded_hamming_code.extend(cleaned_hamming_bits)

            data_as_bits = data_as_bits[number_of_data_and_redundant_bits:]

            if HammingErrorCorrection.ignore_remaining_bits(data_as_bits):
                break

        decoded_hamming_code_byte = HammingErrorCorrection.convert_bits_to_bytes(decoded_hamming_code)

        decoded_hamming_code_byte_string = b''.join(decoded_hamming_code_byte)

        return decoded_hamming_code_byte_string

    @staticmethod
    def convert_bytes_to_bits(list_with_bytes: list) -> list:

        list_with_bits = []

        for value in list_with_bytes:
            list_with_bits = [int(i) for i in str(np.binary_repr(value, 8))]

        return list_with_bits

    @staticmethod
    def add_placeholder_redundant_bits(list_with_bits: list, number_of_data_and_redundant_bits: int) -> list:

        j, k, hamming_code_with_placeholders = 0, 0, []

        for i in range(0, number_of_data_and_redundant_bits):
            position_of_next_redundant_bit = 2 ** j

            if position_of_next_redundant_bit == i + 1:
                hamming_code_with_placeholders.append(0)
                j += 1
            else:
                hamming_code_with_placeholders.append(int(list_with_bits[k]))
                k += 1

            i += 1

        return hamming_code_with_placeholders

    @staticmethod
    def calculate_values_for_redundant_bits(redundant_bits: int, number_of_data_and_redundant_bits: int,
                                            hamming_code: list):

        number_of_iterations, sum_of_bit_values = 0, 0

        while number_of_iterations < redundant_bits:
            position_of_next_redundant_bit = 2 ** number_of_iterations
            j = position_of_next_redundant_bit - 1

            # Check all relevant bits in the array for their value
            # https://users.cis.fiu.edu/~downeyt/cop3402/hamming.html
            while j < number_of_data_and_redundant_bits:
                for i in range(position_of_next_redundant_bit):
                    sum_of_bit_values += hamming_code[j]
                    j += 1
                    if j >= number_of_data_and_redundant_bits:
                        break

                j += position_of_next_redundant_bit

            # Check if all relevant bits have an even number of 1's
            # If not, update redundant bit value for even parity
            if sum_of_bit_values % 2 != 0:
                hamming_code[position_of_next_redundant_bit - 1] = 1

            sum_of_bit_values = 0
            number_of_iterations += 1

        return hamming_code

    @staticmethod
    def get_bytes(bits: iter) -> bytes:

        done = False
        while not done:
            byte = 0
            for _ in range(0, 8):
                try:
                    bit = next(bits)
                except StopIteration:
                    bit = 0
                    done = True
                byte = (byte << 1) | bit
            yield byte

    @staticmethod
    def convert_bits_to_bytes(hamming_code: list) -> list:

        byte_array, number_of_iterations = [], 0

        for b in HammingErrorCorrection.get_bytes(iter(hamming_code)):
            number_of_iterations += 1
            byte_array.append(bytes([b]))

        number_of_bytes = len(hamming_code) / 8

        # Remove possible empty byte that can occur
        if number_of_bytes + 1 == number_of_iterations:
            byte_array = byte_array[:-1]

        return byte_array

    @staticmethod
    def remove_all_redundant_bits(list_of_hamming_bits: list, redundant_bits: int) -> list:

        number_of_iterations = 0

        while number_of_iterations < redundant_bits:
            position_of_next_redundant_bit = 2 ** number_of_iterations - 1 - number_of_iterations
            del list_of_hamming_bits[position_of_next_redundant_bit]
            number_of_iterations += 1

        return list_of_hamming_bits

    @staticmethod
    def ignore_remaining_bits(decoded_hamming_code: list) -> bool:

        bit_sum = 0

        for bit in decoded_hamming_code:
            bit_sum += bit

        if bit_sum == 0:
            return True

        return False
