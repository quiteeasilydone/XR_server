// const express = require("express");
// var db = require('../lib/db.js'); // db 선언
// const router = express.Router();

function return_sql(infra, sensor_name,start,end,transform) {
    // console.log(query);
    
    // Serial Number of Infrastructure
    // let infrastructure = query.infra;
    
    // Error Type -1: all, 0: Normal, 1~3: type

    // TODO: Sensors can be list so we need to split it


    // Transform (Normal, FFT, RMS) <string>
    
    // Query start, end Index


    // base Query string
    let sql = "SELECT " + sensor_name + " FROM test_data";

    // Query start, end Index
    let indices = " WHERE id BETWEEN " + start + " AND " + end;
    
    // Query all sensors
    // sql += " WHERE label = " + sensor;
        // Query all sensors

    // else if (transform != "Normal"){
    //     // Query specific sensors
        
    //     // Query specific transform
    //     switch (transform){
    //         case "FFT":
    //             // FLASK
    //             break;
    //         case "RMS":
    //             // FLASK
    //             // Query RMS
    //             break;
    //         default:

    //             // Query Normal
    //             break;
    //     }
        
    // }

    sql += indices;
    
    console.log(sql);
    return sql
};

module.exports.return_query = return_sql; // main 함수에 router 인식