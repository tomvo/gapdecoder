const { aes_decrypt_buffer, decrypt_image, fromhex, tohex } = require("../decryption.js");
const assert = require("assert");
const fs = require('fs').promises;

async function test_aes_decrypt_buffer() {
    const input = "e5c820455856b03589de7809179dda78ce2b41b9b6db85d325cea350d02babe0";

    assert.equal(
        "010101010c0c0c0c0c0c0c0c0c0c0c0c10101010101010101010101010101010",
        tohex(await aes_decrypt_buffer(fromhex(input)))
    );
}

async function test_decrypt_image() {
    const input = fromhex(
        "0A0A0A0A" + // magic header
        "BABAC0C0" + // clear prefix
        "10000000" + // little endian encrypted data length
        "01010101010101010101010101010101" + // encrypted data
        "DEADBEAF" + // clear suffix
        "04000000" // offset to encrypted data length
    );
    expected = 'babac0c0' +
        'ca251118030ff9aff186bdccbce26a4c' +
        'deadbeaf';
    assert.equal(expected, tohex(await decrypt_image(input)));
}

async function test_decrypt_real_tile() {
    const ciphered = await fs.readFile(__dirname + "/tile_ciphered.bin");
    const expected = await fs.readFile(__dirname + "/tile.jpg");
    const clear = await decrypt_image(ciphered);
    assert.equal(tohex(expected), tohex(clear));
}

test_aes_decrypt_buffer();
test_decrypt_image();
test_decrypt_real_tile();