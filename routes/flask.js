const express = require('express');
const https = require('https');
// var request = require('request');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
var db = require('../lib/db.js');
const return_query = require('../lib/acquireData.js');
const router = express.Router();

const keyPath = path.join('./key.pem');
const certPath = path.join('./cert.pem');

const httpsAgent = new https.Agent({
    rejectUnauthorized: false, // 자체 서명된 인증서를 사용할 경우 필요
    cert: fs.readFileSync(certPath),
    key: fs.readFileSync(keyPath)
  });

router.post('/', async(req, res) => {
    try{
        let body = req.body;
        const sensor_name = body.sensor;
        const infra = body.infra;
        const transform = body.transform;
        const start = body.start;
        const end = body.end;
    // const vibe_data = body.file_name;

        const flaskServerUrl = 'https://127.0.0.1:5000/analyze';
        sql = return_query.return_query(infra, sensor_name,start,end);
        const dbResult = await new Promise((resolve, reject) => {
            db.query(sql, (err, result, fields) => {
                if (err) reject(err);
                resolve(result);
            });
        });

        console.log(dbResult);
        const response = await axios.post(flaskServerUrl, { data: dbResult, transform }, {
            params: { sensor: sensor_name },
            httpsAgent
        });
        res.json(response.data);
    } catch (error) {
        console.error(error);
        res.status(500).send('Error sending data to Flask server: ' + error);
    }
    // db 접근
    //     db.query(sql, (err, result, fields) => {
    //         if (err) throw err;
    //         console.log(result);
    //         const response = axios.post(flaskServerUrl, { data: result, transform }, {
    //             params: { sensor: sensor_name }
    //             }, httpsAgent).then(response => console.log(response.data), res.json(response.data)).catch(error => console.error(error));
    //     });
    // } catch (error) {
    //     res.status(500).send('Error sending data to Flask server: ' + error);
    // }
    // let body = req.body;
    // const sensor_name = body.sensor || 'sensor_one';
    // // const vibe_data = body.file_name;

    // const flaskServerUrl = 'http://165.246.44.131:5000/fourier';

    // // db 접근
    // db.query('select * from test_data limit 10', (err, result, fields) => {
    //     if (err) throw err;
    //     console.log(result);
    //     const response = await axios.post(flaskServerUrl, { data: result }, {
    //         params: { sensor: sensor_name }
    //         });
    //     res.json(response.data);
    // });
});

module.exports = router;