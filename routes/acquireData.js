const express = require("express");
var db = require('../lib/db.js'); // db 선언

const router = express.Router();

router.get('/', (req, res) => {
    // Serial Number of Infrastructure
    let infrastructure = req.params.infra;
    
    // Error Type -1: all, 0: Normal, 1~3: type
    let sensors = req.params.sensors;
    
    //Transform (FFT, RMS)
    let transform = req.params.transform;
    
    // Query start, end Index
    let start = req.params.start;
    let end = req.params.end;
    

    if (sensors == -1) {
        
    } else {
        
    }
    
    db.query('SELECT')
});