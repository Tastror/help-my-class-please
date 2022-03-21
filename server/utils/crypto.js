const crypto = require('crypto')

exports.random = (l = 32) => crypto.randomBytes(l).toString('base64')

exports.md5 = (msg) => crypto.createHash('md5').update(msg).digest('base64').substr(7, 10).replace(/\//g, '_').replace(/\+/g, '-').replace(/\=/g, '')

exports.short = str => str.substr(0, 10).replace(/\//g, '_').replace(/\+/g, '-')

exports.sha256 = (msg) => crypto.createHash('sha256').update(msg).digest('base64')

exports.HS256 = (msg, secret) => crypto.createHmac('sha256', secret).update(msg).digest('base64')