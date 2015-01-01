#!/usr/bin/env node

var fs = require('fs')
  , http = require('http')
  , path = require('path')
  , url = require('url')

var browserify = require('browserify')
  , ractify = require('ractify')

var port = process.env.PORT || 8001

var SRC_DIR = process.env.SRC_DIR || path.join(__dirname, '..', 'src')
  , DEBUG = process.env.DEBUG || false

module.exports = http.createServer(handler).listen(port, function() {
  this.emit('ready')
})

console.log('server listening on ' + port)

function handler(req, res) {
  var furl = url.parse(req.url).pathname
    , fpath
    , contentType

  if(furl === '/') {
    furl = '/index.html'
  }

  fpath = path.join(SRC_DIR, furl)

  switch(path.extname(fpath)) {
    case '.html':
    case '.htm':
      contentType = 'text/html'
      serveFile(fpath)

      break

    case '.js':
      contentType = 'text/javascript'
      serveBrowserify(fpath)

      break

    case '.css':
      contentType = 'text/css'
      serveFile(fpath)

      break

    default:
      contentType = 'text/unknown'
      serveFile(fpath)
  }

  function serveFile(file) {
    var fstream

    console.log('serving file: ' + file)
    fstream = fs.createReadStream(file)
    fstream.on('error', e404)

    res.writeHead(200, {'Content-Type': contentType})
    fstream.pipe(res)
  }

  function serveBrowserify(file) {
    var opts = {
          debug: DEBUG
      }
      , b = browserify(file, opts)
      , bundle

    b.transform(ractify)

    console.log('browserifying file: ' + file)
    bundle = b.bundle()
    bundle.on('error', e500)

    res.writeHead(200, {'Content-Type': contentType})
    bundle.pipe(res)
  }

  function e404() {
    console.log('not found: ' + fpath)
    res.writeHead(404)
    res.end('not found')
  }

  function e500(err) {
    console.log('error: ' + err)
    res.writeHead(500)
    res.end(err.message)
  }
}
