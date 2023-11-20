const express = require('express');
// var request = require('request');
const axios = require('axios');
var db = require('../lib/db.js');
const router = express.Router();

router.post('/', (req, res) => {
    try{
        let body = req.body;
        const sensor_name = body.sensor;
    // const vibe_data = body.file_name;

        const flaskServerUrl = 'http://165.246.44.131:5000/fourier';

    // db 접근
        db.query('select * from test_data limit 1000', async(err, result, fields) => {
            if (err) throw err;
            console.log(result);
            const response = await axios.post(flaskServerUrl, { data: result }, {
                params: { sensor: sensor_name }
                });
            res.json(response.data);
        });
    } catch (error) {
        res.status(500).send('Error sending data to Flask server: ' + error);
    }
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