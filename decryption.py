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

magics = [bytes.fromhex(s) for s in (
    '000e1c123836242a707e6c624846545ae0eefcf2d8d6c4ca909e8c82a8a6b4badbd5c7c9e3edfff1aba5b7b9939d8f813b352729030d1f114b'
    '455759737d6f61ada3b1bf959b8987ddd3c1cfe5ebf9f74d43515f757b69673d33212f050b191776786a644e40525c06081a143e30222c9698'
    '8a84aea0b2bce6e8faf4ded0c2cc414f5d537977656b313f2d230907151ba1afbdb39997858bd1dfcdc3e9e7f5fb9a948688a2acbeb0eae4f6'
    'f8d2dccec07a746668424c5e500a041618323c2e20ece2f0fed4dac8c69c92808ea4aab8b60c02101e343a28267c72606e444a585637392b25'
    '0f01131d47495b557f71636dd7d9cbc5efe1f3fda7a9bbb59f91838d',
    '000b161d2c273a3158534e45747f6269b0bba6ad9c978a81e8e3fef5c4cfd2d97b706d66575c414a2328353e0f041912cbc0ddd6e7ecf1fa93'
    '98858ebfb4a9a2f6fde0ebdad1ccc7aea5b8b38289949f464d505b6a617c771e1508033239242f8d869b90a1aab7bcd5dec3c8f9f2efe43d36'
    '2b20111a070c656e737849425f54f7fce1eadbd0cdc6afa4b9b28388959e474c515a6b607d761f1409023338252e8c879a91a0abb6bdd4dfc2'
    'c9f8f3eee53c372a21101b060d646f727948435e55010a171c2d263b3059524f44757e6368b1baa7ac9d968b80e9e2fff4c5ced3d87a716c67'
    '565d404b2229343f0e051813cac1dcd7e6edf0fb9299848fbeb5a8a3',
    '000d1a1734392e236865727f5c51464bd0ddcac7e4e9fef3b8b5a2af8c81969bbbb6a1ac8f829598d3dec9c4e7eafdf06b66717c5f52454803'
    '0e1914373a2d206d60777a5954434e05081f12313c2b26bdb0a7aa8984939ed5d8cfc2e1ecfbf6d6dbccc1e2eff8f5beb3a4a98a87909d060b'
    '1c11323f28256e6374795a57404ddad7c0cdeee3f4f9b2bfa8a5868b9c910a07101d3e332429626f7875565b4c41616c7b7655584f42090413'
    '1e3d30272ab1bcaba685889f92d9d4c3ceede0f7fab7baada0838e9994dfd2c5c8ebe6f1fc676a7d70535e49440f0215183b36212c0c01161b'
    '3835222f64697e73505d4a47dcd1c6cbe8e5f2ffb4b9aea3808d9a97',
    '0009121b242d363f48415a536c657e779099828bb4bda6afd8d1cac3fcf5eee73b3229201f160d04737a6168575e454caba2b9b08f869d94e3'
    'eaf1f8c7ced5dc767f646d525b40493e372c251a130801e6eff4fdc2cbd0d9aea7bcb58a8398914d445f5669607b72050c171e2128333addd4'
    'cfc6f9f0ebe2959c878eb1b8a3aaece5fef7c8c1dad3a4adb6bf8089929b7c756e6758514a43343d262f1019020bd7dec5ccf3fae1e89f968d'
    '84bbb2a9a0474e555c636a71780f061d142b2239309a938881beb7aca5d2dbc0c9f6ffe4ed0a0318112e273c35424b5059666f747da1a8b3ba'
    '858c979ee9e0fbf2cdc4dfd63138232a151c070e79706b625d544f46',
)]

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


def get_new_bytes(bytes, new_bytes, index):
    """
    >>> get_new_bytes(bytearray(b"0123456789abcdef"), [], 0)
    [210, 184, 209, 186, 238, 125, 246, 208, 49, 139, 15, 174, 107, 113, 6, 202]
    """
    # Split the bytes down into groups of 4
    state_matrix_4x4 = [bytes[index + i:index + i + 4] for i in range(0, 16, 4)]
    # Loop through magic table
    for n, key in enumerate(key_schedule):
        if n > 1:  # Xor the split bytes with the magic lists
            state_matrix_4x4 = xor_bytes_by_magic_lists(state_matrix_4x4)
        if n > 0:  # Map the bytes
            state_matrix_4x4 = inv_shift_rows_and_inv_sub_bytes(state_matrix_4x4)
        # Xor again by the table index
        state_matrix_4x4 = add_round_key(state_matrix_4x4, key)

    # Add the new bytes to the list
    for a in range(4):
        new_bytes += state_matrix_4x4[a]
    return new_bytes


def xor_bytes_by_magic_lists(split_bytes):
    """
    >>> xor_bytes_by_magic_lists([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]])
    [[43, 60, 33, 50], [103, 80, 125, 70], [35, 52, 41, 58], [255, 136, 197, 174]]
    """
    return [[updated_split_byte(chunk, j) for j in range(4)] for chunk in split_bytes]


def updated_split_byte(chunk, j):
    return reduce(xor, (magics[i - j][c] for i, c in enumerate(chunk)))


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
        new_bytes = get_new_bytes(bytes, new_bytes, index)
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
