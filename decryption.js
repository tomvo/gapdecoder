const subtle = (typeof crypto === 'undefined') ? require("./subtle.js") : crypto.subtle;

function fromhex(h) {
    return Uint8Array.from(h.match(/[0-9a-fA-F]{2}/g).map(x => parseInt(x, 16)))
}

function tohex(b) {
    return Array.from(b).map(x => x.toString(16).padStart(2, '0')).join('')
}

aes_key_promise = subtle.importKey("raw", fromhex('5b63db113b7af3e0b1435556c8f9530c'), "AES-CBC", true, ["encrypt", "decrypt"]);
aes_iv = fromhex('71e70405353a778bfa6fbc30321b9592');

async function aes_decrypt_buffer(buffer) {
    const algorithm = { name: "AES-CBC", iv: aes_iv };
    const key = await aes_key_promise;
    const decrypted = await subtle.decrypt(algorithm, key, buffer);
    return new Uint8Array(decrypted);
}

if (typeof module !== "undefined") {
    module.exports = { aes_decrypt_buffer, fromhex, tohex }
}