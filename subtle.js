/// This is not a proper polyfill for the Web Crypto API in node
/// This is the minimal required code to make it work in our specific case

const crypto = require('crypto');

async function importKey(_, key) {
    return key;
}

function compute(obj, buffer) {
    const out = obj.update(buffer);
    const final = obj.final()
    return Buffer.concat([out, final]);
}

async function decrypt({ iv }, key, buffer) {
    const decipher = crypto.createDecipheriv("aes-128-cbc", key, iv);
    return compute(decipher, buffer);
}

async function encrypt({ iv }, key, buffer) {
    const cipher = crypto.createCipheriv("aes-128-cbc", key, iv);
    return compute(cipher, buffer);
}

async function sign(alg, key, buffer) {
    const hmac = crypto.createHmac('sha1', key);
    return hmac.update(buffer).digest();
}

module.exports = { importKey, decrypt, encrypt, sign }