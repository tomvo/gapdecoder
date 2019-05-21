#!/usr/bin/env python3
# coding: utf-8

import base64
import hashlib
import re

import lxml.html
from lxml import etree

import requests

from decryption import decrypt

IV = [123, 43, 78, 35, 222, 44, 197, 197]
IV_LENGTH = 64
IV_XORS = (54, 92)


def encode_string(s, iv, iv_len):
    """
    >>> encode_string("hello", IV, IV_LENGTH).hex()
    '871779485cab314d51fa8265fe3b4a96194ace2e'
    >>> encode_string("&&&", IV, IV_LENGTH).hex()
    '914239c61092138b4f3e90e4f2db3d33901bd094'
    """
    previous = s.encode('utf-8')
    for xor in IV_XORS:
        full_iv = iv + [0] * (iv_len - len(IV))
        h = hashlib.sha1()
        h.update(bytes(xor ^ x for x in full_iv))
        h.update(previous)
        previous = h.digest()
    return previous


def fetch_tile(path, token, x, y, z):
    sign_path = '%s=x%s-y%s-z%s-t%s' % (path, x, y, z, token)
    encoded = encode_string(sign_path, IV, IV_LENGTH)
    signature_bytes = base64.b64encode(encoded)[:-1].replace(b'+', b'_').replace(b'/', b'_')
    signature = signature_bytes.decode('utf-8')
    image_url = 'https://lh3.googleusercontent.com/%s=x%s-y%s-z%s-t%s' % (path, x, y, z, signature)
    r = requests.get(image_url)
    return decrypt(r.content)


def load_tiles(url):
    r = requests.get(url)
    image_slug, image_id = url.split('?')[0].split('/')[-2:]
    image_name = '%s - %s' % (image_slug, image_id)

    tree = lxml.html.fromstring(r.text)
    image_url = tree.xpath("//meta[@property='og:image']/@content")[0]
    meta_info_tree = etree.fromstring(requests.get(image_url + '=g').content)
    tile_info = [x.attrib for x in meta_info_tree.xpath('//pyramid_level')]
    path = image_url.split('/')[3]
    token = re.findall(r'"%s","([^"]+)"' % (image_url.split(':', 1)[1],), r.text)[0]

    z = 7
    tile = tile_info[z]
    for x in range(int(tile['num_tiles_x'])):
        for y in range(int(tile['num_tiles_y'])):
            fn = '%s %sx%sx%s.jpg' % (image_name, x, y, z)
            with open(fn, 'wb') as f:
                f.write(fetch_tile(path, token, x, y, z))


if __name__ == '__main__':
    load_tiles('https://artsandculture.google.com/asset/lady-with-an-ermine/HwHUpggDy_HxNQ')
