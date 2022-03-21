module.exports = f => async (req, resp, next) => {
  try {
    const res = await f(req)
    if (!res) next()
    else {
      if (!res[1]) res[1] = 200
      resp.status(res[1]).send(res[0])
    }
  } catch (e) {
    resp.status(500).send('System Error: ' + e.toString())
  }
}
