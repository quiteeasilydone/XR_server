const express = require("express");
var db = require('../lib/db.js'); // db 선언
const router = express.Router();

router.get('/', (req, res) => {
    var query = req.query;
    console.log(query);
    
    // Serial Number of Infrastructure
    let infrastructure = query.infra;
    
    // Error Type -1: all, 0: Normal, 1~3: type
    let sensors = query.sensors;

    // TODO: Sensors can be list so we need to split it


    // Transform (Normal, FFT, RMS) <string>
    let transform = query.transform;
    
    // Query start, end Index
    let start = query.start;
    let end = query.end;
    
    // base Query string
    let sql = "SELECT";

    // Query start, end Index
    let indices = " WHERE id BETWEEN " + db.escape(start) + " AND " + db.escape(end);
    
    // Query all sensors
    if (sensors == -1) {
        sql += " * FROM test_data";
        // Query all sensors
    } else if (transform != "Normal"){
        // Query specific sensors
        
        // Query specific transform
        switch (transform){
            case "FFT":
                // FLASK
                break;
            case "RMS":
                // FLASK
                // Query RMS
                break;
            default:

                // Query Normal
                break;
        }
        
    }

    sql += indices;
    console.log(sql);
    db.query(sql, (err, result, fields) => {
        if (err) throw err;
        console.log(result);
        res.json(result);
    });
});

module.exports = router; // main 함수에 router 인식