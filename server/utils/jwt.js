const crypto = require('crypto')
const c = {
  padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
  saltLength: crypto.constants.RSA_PSS_SALTLEN_DIGEST
}
const key = {}

function setKey (k) {
  key.pk = k.pk
  key.sk = k.sk
}

const buffer2Base64url = b => b.toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
const base64url2Buffer = v => {
  while (v.length % 4) v += '='
  return Buffer.from(v.replace(/\-/g, '+').replace(/\_/g, '/'), 'base64')
}
const str2Base64url = s => buffer2Base64url(Buffer.from(s))

function sign (payload, sk = key.sk) {
  const data = str2Base64url('{"alg":"PS256","typ":"JWT"}') + '.' + str2Base64url(JSON.stringify(payload))
  return data + '.' + buffer2Base64url(crypto.sign('rsa-sha256', Buffer.from(data), { key: sk, ...c }))
}

function verify (jwt, pk = key.pk) {
  try {
    const raw = jwt.split('.')
    if (!crypto.verify('rsa-sha256', Buffer.from(raw[0] + '.' + raw[1]),
      { key: pk, ...c }, base64url2Buffer(raw[2]))) return false
    return JSON.parse(base64url2Buffer(raw[1]).toString())
  } catch {
    return false
  }
}

module.exports = {
  sign, verify, str2Base64url, base64url2Buffer, setKey
}