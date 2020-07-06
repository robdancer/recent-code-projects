var express = require('express');
var verify = require('../verify.js');
var router = express.Router();

const yearExpire = 31536000000;

/* GET login page. */
router.get('/', function(req, res, next) {
    if(req.signedCookies.loggedin === 'true') {
        res.redirect('/list/');
    } else {
        res.render('login', { title: 'Login', fail: false });
    }    
});

/* POST credentials check */
router.post('/', function(req, res, next) {
    if(verify.verifyCredentials(req.body.password)) {
        res.cookie('loggedin', true, {signed: true, sameSite: 'Strict', maxAge: yearExpire});
        if(req.query.after) {
            res.redirect(decodeURIComponent(req.query.after));
        } else {
            res.redirect('/list/');
        }
    } else {
        res.render('login', {title: 'Login', fail: true})
    }
});

module.exports = router;
