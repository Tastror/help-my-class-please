const express = require('express')
const axios = require('axios')
const jwt = require('./utils/jwt.js')
const H = require('./H.js')

const app = express()
app.disable('x-powered-by') // hide express identity

app.use('/', express.static('/opt/matrix-web'))

const api = express.Router() // router
app.use(express.json())
app.use('/api', api) // register with middleware

api.use('/configuration', require('./controllers/configuration.js'))

app.listen(3001, () => {
  console.log('# Server started on port 3001')
})

axios.get('https://cn.api.aauth.link/app/matrix')
  .then(r => {
    console.log('# got pk from aauth')
    jwt.setKey(r.data)
  })
  .catch(console.error)