module.exports = function btoa(s) {
    return Buffer.from(s, 'binary').toString('base64');
}