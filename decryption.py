#!/usr/bin/env python3
# coding: utf-8
import struct
from Crypto.Cipher import AES

aes_key = bytes.fromhex('5b63db113b7af3e0b1435556c8f9530c')
aes_iv = bytes.fromhex('71e70405353a778bfa6fbc30321b9592')


def aes_decrypt_buffer(buffer):
    """
    >>> aes_decrypt_buffer(b"0123456789abcdef"*2).hex()
    'a35fd5bfdb47815bcbe4b39e596a9358e289e389da48c0e709b26ecc081563ac'
    """
    cipher = AES.new(aes_key, AES.MODE_CBC, iv=aes_iv)
    return cipher.decrypt(buffer)


def bytes_to_number(buffer, index):
    return struct.unpack_from("<i", buffer, index)[0]


def decrypt(image):
    # return if the encryption marker isn't present at the start of the file
    if image[:4] != b"\x0A\x0A\x0A\x0A":
        return image

    # Convert the image to a array of bytes (0 -> 255) (for insertion, maths etc)
    byte_list = bytearray(image)

    # Use the last 4 bytes to get the index of the bytes to be replaced
    index = bytes_to_number(byte_list, len(byte_list) - 4)

    # Trim out the encryption marker and info bytes
    byte_list = byte_list[4:-4]

    # How many bytes to replace
    replace_num = bytes_to_number(byte_list, index)

    # Delete the 4 bytes at the start
    del byte_list[index:index + 4]

    # The bytes to replace
    to_replace = byte_list[index:index + replace_num]

    # Get the replacement bytes
    replacement = aes_decrypt_buffer(to_replace)
    # Replace the bytes!
    byte_list[index:index + replace_num] = replacement

    # Convert back into bytes
    return bytes(byte_list)
