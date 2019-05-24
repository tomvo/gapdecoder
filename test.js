const { aes_decrypt_buffer, fromhex, tohex } = require("./decryption.js");
const assert = require("assert");



async function test_aes_decrypt_buffer() {
    const input = "e5c820455856b03589de7809179dda78ce2b41b9b6db85d325cea350d02babe0";

    assert.equal(
        "010101010c0c0c0c0c0c0c0c0c0c0c0c",
        tohex(await aes_decrypt_buffer(fromhex(input)))
    );
}


test_aes_decrypt_buffer();