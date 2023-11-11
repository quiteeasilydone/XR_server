const express = require("express");
var db = require('../lib/db.js'); // db 선언
const router = express.Router();

router.get('/', (req, res) => {
    db.query('select * from test_data limit 10', (err, result, fields) => {
        if (err) throw err;
        console.log(result);
        res.json(result);
    });
});

module.exports = router; // main 함수에 router 인식