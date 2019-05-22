#!/usr/bin/env python3
# coding: utf-8
from functools import reduce
from operator import xor
import struct

aes_inverse_s_box = bytes.fromhex(
    '52096ad53036a538bf40a39e81f3d7fb7ce339829b2fff87348e4344c4dee9cb547b9432a6c2233dee4c950b42fac34e082ea16628d924b276'
    '5ba2496d8bd12572f8f66486689816d4a45ccc5d65b6926c704850fdedb9da5e154657a78d9d8490d8ab008cbcd30af7e45805b8b34506d02c'
    '1e8fca3f0f02c1afbd0301138a6b3a9111414f67dcea97f2cfcef0b4e67396ac7422e7ad3585e2f937e81c75df6e47f11a711d29c5896fb762'
    '0eaa18be1bfc563e4bc6d279209adbc0fe78cd5af41fdda8338807c731b11210592780ec5f60517fa919b54a0d2de57a9f93c99cefa0e03b4d'
    'ae2af5b0c8ebbb3c83539961172b047eba77d626e169146355210c7d'
)


def gmul(a, b):
    p = 0
    for c in range(8):
        if b & 1:
            p ^= a
        a <<= 1
        if a & 0x100:
            a ^= 0x11b
        b >>= 1
    return p


aes_gmul_table = [bytes(gmul(f, x) for x in range(0, 0x100)) for f in (0x0e, 0x0b, 0x0d, 0x09)]

magic_xor = bytes.fromhex('71e70405353a778bfa6fbc30321b9592')
key_schedule = [bytes.fromhex(x) for x in (
    'aec578ad59ae2a73fe7fc045e119e8b5',
    'abf1f46df76b52dea7d1ea361f6628f0',
    '19d440015c9aa6b350bab8e8b8b7c2c6',
    '4e0e719a454ee6b20c201e5be80d7a2e',
    'd64decf30b409728496ef8e9e42d6475',
    'ec933266dd0d7bdb422e6fc1ad439c9c',
    'c09e7eb9319e49bd9f23141aef6df35d',
    'e70adee8f1003704aebd5da7704ee747',
    'eefe3ff5160ae9ec5fbd6aa3def3bae0',
    'c38e25f9f8f4d61949b7834f814ed043',
    '5b63db113b7af3e0b1435556c8f9530c'
)]


def get_new_bytes(bytes, index):
    """
    >>> get_new_bytes(bytearray(b"0123456789abcdef"), 0)
    [210, 184, 209, 186, 238, 125, 246, 208, 49, 139, 15, 174, 107, 113, 6, 202]
    """
    # Split the bytes down into groups of 4
    state_matrix_4x4 = [bytes[index + i:index + i + 4] for i in range(0, 16, 4)]
    # Loop through magic table
    for n, key in enumerate(key_schedule):
        if n > 1:  # Xor the split bytes with the magic lists
            state_matrix_4x4 = inv_mix_columns(state_matrix_4x4)
        if n > 0:  # Map the bytes
            state_matrix_4x4 = inv_shift_rows_and_inv_sub_bytes(state_matrix_4x4)
        # Xor again by the table index
        state_matrix_4x4 = add_round_key(state_matrix_4x4, key)

    # Add the new bytes to the list
    return sum(state_matrix_4x4, [])


def inv_mix_columns(split_bytes):
    """
    >>> inv_mix_columns([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]])
    [[43, 60, 33, 50], [103, 80, 125, 70], [35, 52, 41, 58], [255, 136, 197, 174]]
    """
    return [[updated_split_byte(chunk, j) for j in range(4)] for chunk in split_bytes]


def updated_split_byte(chunk, j):
    return reduce(xor, (aes_gmul_table[i - j][c] for i, c in enumerate(chunk)))


def add_round_key(split_bytes, key):
    """
    >>> add_round_key([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]], key_schedule[0])
    [[175, 199, 123, 169], [92, 168, 45, 123], [247, 117, 203, 73], [236, 23, 231, 165]]
    """
    return [[split_bytes[y][x] ^ key[y * 4 + x] for x in range(4)] for y in range(4)]


def inv_shift_rows_and_inv_sub_bytes(split_bytes):
    """
    >>> inv_shift_rows_and_inv_sub_bytes([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]])
    [[9, 215, 158, 191], [54, 106, 251, 129], [64, 165, 213, 124], [243, 163, 56, 48]]
    """
    return [[aes_inverse_s_box[split_bytes[y - x][x]] for x in range(4)] for y in range(4)]


def get_replacement(bytes):
    """
    >>> bytes(get_replacement(b"0123456789abcdef"*2)).hex()
    'a35fd5bfdb47815bcbe4b39e596a9358e289e389da48c0e709b26ecc081563ac'
    """
    # Setup up list of new bytes
    new_bytes = []
    # Loop through chunks of 16
    for index in range(0, len(bytes), 16):
        # Get the new bytes
        new_bytes += get_new_bytes(bytes, index)
        # Get the bytes to xor with
        xor = magic_xor if index == 0 else bytes
        # xor the new bytes
        for i in range(16):
            new_bytes[index + i] ^= xor[i]
    return new_bytes


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
    replacement = get_replacement(to_replace)
    # Replace the bytes!
    byte_list[index:index + replace_num] = replacement

    # Convert back into bytes
    return bytes(byte_list)
