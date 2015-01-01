var Ractive = require('ractive')
  , template = require('./template.ract').template
  , ractive = new Ractive({
        el: '#container'
      , template: template
    })
