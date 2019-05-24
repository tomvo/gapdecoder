const subtle = (typeof crypto === 'undefined') ? require("./subtle.js") : crypto.subtle;

function fromhex(h) {
    return Uint8Array.from(h.match(/[0-9a-fA-F]{2}/g).map(x => parseInt(x, 16)))
}

function tohex(b) {
    return Array.from(b).map(x => x.toString(16).padStart(2, '0')).join('')
}

const aes_key_promise = subtle.importKey("raw", fromhex('5b63db113b7af3e0b1435556c8f9530c'), "AES-CBC", true, ["encrypt", "decrypt"]);
const aes_iv = fromhex('71e70405353a778bfa6fbc30321b9592');

const algorithm = { name: "AES-CBC", iv: aes_iv };

// We need a padding because subtle exposes only
// PKCS#7 padded crypto primitives
const pad = aes_key_promise.then(key =>
    subtle.encrypt(algorithm, key,
        new Uint8Array(32).fill(16))
);

async function aes_decrypt_buffer(buffer) {
    const key = await aes_key_promise;
    // Pad the input
    const c = concat(buffer, await pad);
    const decrypted = await subtle.decrypt(algorithm, key, c);
    // Un-pad the output
    return new Uint8Array(decrypted).slice(0, decrypted.byteLength - 32);
}

function concat(...arrs) {
    const l = arrs.map(a => a.byteLength).reduce((x, y) => x + y, 0);
    const r = new Uint8Array(l);
    for (let i = 0, offset = 0; i < arrs.length; i++) {
        r.set(arrs[i], offset);
        offset += arrs[i].byteLength;
    }
    return r;
}

async function decrypt_image({ buffer }) {
    // The file is composed of a constant header, a body,
    // and a last 4-byte word indicating the start of the encrypted part
    const view = new DataView(buffer);

    // return if the encryption marker isn't present at the start of the file
    if (view.getUint32(0) !== 0x0A0A0A0A) return image;

    const index = view.getUint32(view.byteLength - 4, true);
    const clear_prefix = new Uint8Array(view.buffer, 4, index);
    const replace_count = view.getUint32(4 + index, true);
    const encrypted = new Uint8Array(view.buffer, 4 + index + 4, replace_count);
    const suffix_start = 4 + index + 4 + replace_count;
    const clear_suffix = new Uint8Array(view.buffer, suffix_start, view.byteLength - suffix_start - 4);
    return concat(clear_prefix, await aes_decrypt_buffer(encrypted), clear_suffix);
}

if (typeof module !== "undefined") {
    module.exports = { aes_decrypt_buffer, decrypt_image, fromhex, tohex }
}