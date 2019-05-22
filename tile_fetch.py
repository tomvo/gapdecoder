#!/usr/bin/env python3
# coding: utf-8

import base64
import hmac
import re

import lxml.html
from lxml import etree

import requests

from decryption import decrypt

IV = bytes.fromhex("7b2b4e23de2cc5c5")


def compute_url(path, token, x, y, z):
    """
    >>> path = 'wGcDNN8L-2COcm9toX5BTp6HPxpMPPPuxrMU-ZL-W-nDHW8I_L4R5vlBJ6ITtlmONQ'
    >>> token = 'KwCgJ1QIfgprHn0a93x7Q-HhJ04'
    >>> compute_url(path, token, 0, 0, 7)
    'https://lh3.googleusercontent.com/wGcDNN8L-2COcm9toX5BTp6HPxpMPPPuxrMU-ZL-W-nDHW8I_L4R5vlBJ6ITtlmONQ=x0-y0-z7-tHeJ3xylnSyyHPGwMZimI4EV3JP8'
    """
    sign_path = b'%s=x%d-y%d-z%d-t%s' % (path.encode('utf8'), x, y, z, token.encode('utf8'))
    encoded = hmac.new(IV, sign_path, 'sha1').digest()
    signature_bytes = base64.b64encode(encoded, b'__')[:-1]
    signature = signature_bytes.decode('utf-8')
    return 'https://lh3.googleusercontent.com/%s=x%s-y%s-z%s-t%s' % (path, x, y, z, signature)


def fetch_tile(path, token, x, y, z):
    image_url = compute_url(path, token, x, y, z)
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
    part = image_url.split(':', 1)[1]
    token_regex = r'"{}","([^"]+)"'.format(part)
    token = re.findall(token_regex, r.text)[0]

    z = 7
    tile = tile_info[z]
    for x in range(int(tile['num_tiles_x'])):
        for y in range(int(tile['num_tiles_y'])):
            fn = '%s %sx%sx%s.jpg' % (image_name, x, y, z)
            with open(fn, 'wb') as f:
                f.write(fetch_tile(path, token, x, y, z))


if __name__ == '__main__':
    load_tiles('https://artsandculture.google.com/asset/lady-with-an-ermine/HwHUpggDy_HxNQ')
