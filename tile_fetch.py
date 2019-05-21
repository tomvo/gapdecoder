import base64
import hashlib
import re

import lxml.html
import requests

from lxml import etree

from decryption import decrypt

IV = [123, 43, 78, 35, 222, 44, 197, 197]
IV_LENGTH = 64


def encode_string(s, iv, iv_len):
    prefix = []
    postfix = []

    for i in range(iv_len):
        v = len(iv) > i and iv[i] or 0
        prefix.append(v ^ 54)
        postfix.append(v ^ 92)

    h = hashlib.sha1()
    h.update(bytearray(prefix))
    h.update(bytearray(s.encode('utf-8')))

    v = h.digest()
    h = hashlib.sha1()
    h.update(bytearray(postfix))
    h.update(v)

    return h.digest()


def fetch_tile(path, token, x, y, z):
    sign_path = '%s=x%s-y%s-z%s-t%s' % (path, x, y, z, token)
    signature = base64.b64encode(
        encode_string(sign_path, IV, IV_LENGTH))[:-1].replace(b'+', b'_').replace(b'/', b'_').decode(
        'utf-8')
    image_url = 'https://lh3.googleusercontent.com/%s=x%s-y%s-z%s-t%s' % (path, x, y, z, signature)
    r = requests.get(image_url)
    return decrypt(r.content)


if __name__ == '__main__':
    url = 'https://artsandculture.google.com/asset/lady-with-an-ermine/HwHUpggDy_HxNQ'
    r = requests.get(url)
    image_slug, image_id = url.split('?')[0].split('/')[-2:]
    image_name = '%s - %s' % (image_slug, image_id)

    tree = lxml.html.fromstring(r.text)
    image_url = tree.xpath("//meta[@property='og:image']/@content")[0]
    tile_info = [x.attrib for x in etree.fromstring(requests.get(image_url + '=g').content).xpath('//pyramid_level')]
    path = image_url.split('/')[3]
    token = re.findall(r'"%s","([^"]+)"' % (image_url.split(':', 1)[1],), r.text)[0]

    z = 7
    tile = tile_info[z]
    for x in range(int(tile['num_tiles_x'])):
        for y in range(int(tile['num_tiles_y'])):
            fn = '%s %sx%sx%s.jpg' % (image_name, x, y, z)
            with open(fn, 'wb') as f:
                f.write(fetch_tile(path, token, x, y, z))
