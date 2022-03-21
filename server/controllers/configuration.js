const fs = require('fs').promises,
  express = require('express'),
  jwt = require('../utils/jwt'),
  H = require('../H')

async function get (req) {
  const uid = req.query.uid // test
  if (!uid) return ['Permission Denied', 403]
  const res = await fs.readFile('./data/' + uid).then(r => JSON.parse(r))
  return [res]
}

async function post (req) {
  const uid = req.query.uid // test
  if (!uid) return ['Permission Denied', 403]
  await fs.writeFile('./data/' + uid, JSON.stringify(req.body))
  return ['success']
}

const router = express.Router()

router.get('/', H(get))
router.post('/', H(post))

module.exports = router
