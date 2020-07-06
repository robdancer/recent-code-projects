var express = require('express');
var fs = require('fs');
var path = require('path');
var router = express.Router();

/* GET login page. */
router.get('/list/*', function(req, res, next) {
    if(req.signedCookies.loggedin === 'true') {
        fs.readdir(path.join('././resource', req.params[0]), {withFileTypes: true}, function(err, files) {
            if (err) {
                if (err.code === "ENOENT") {
                    // Doesn't exist
                    next();
                } else if (err.code === "ENOTDIR") {
                    // Is a file
                    // Send it over
                    res.sendFile(path.join(__dirname, '..', 'resource', req.params[0]));
                } else {
                    next();
                }
            } else {
                // Is a folder
                // Last character *must* be a forward slash for stuff to work
                if(req.url.substr(req.url.length-1) === '/'){
                    // Display contents
                    res.render('list', {title: 'Listing', titles: files});
                } else {
                    // Redirect and add forward slash
                    res.redirect(req.params[0] + '/');
                }

            }
        });      
    } else {
        res.redirect('/login?after=' + encodeURIComponent(req.path));
    }    
});

router.get('/list', function(req, res, next) {
    res.redirect(req.url + '/');
})

module.exports = router;
