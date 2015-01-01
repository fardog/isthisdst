#!/usr/bin/env node

var spawn = require('child_process').spawn
  , path = require('path')

var server = require('./server')
  , args = [
        '--recursive'
      , '--convert-links'
      , '--html-extension'
      , '--no-parent'
      , '--no-host-directories'
      , 'http://localhost:' + (process.env.PORT ? process.env.PORT : 8001) + '/'
    ]
  , wget 

server.on('ready', function() {
  wget = spawn('wget', args, {cwd: path.join(__dirname, '..', 'build/') })
  wget.on('exit', function(code) {
    if (code === 0) {
      console.log('\n\nEverything was successful.')
    }
    process.exit(code)
  })
  wget.stdout.pipe(process.stdout)
  wget.stderr.pipe(process.stderr)
})
