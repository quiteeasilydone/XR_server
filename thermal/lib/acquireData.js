// const express = require("express");
// var db = require('../lib/db.js'); // db 선언
// const router = express.Router();

function return_sql(infra, s) {

    let sql = "SELECT " + sensor_name + ", label FROM test_data";

    let indices = " WHERE id BETWEEN " + start + " AND " + end;


    sql += indices;
    
    // console.log(sql);
    return sql
};

module.exports.return_query = return_sql; // main 함수에 router 인식