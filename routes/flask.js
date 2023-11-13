const express = require('express');
var request = require('request');
const router = express.Router();

router.post('/', function (req, res, next) {
    let body = req.body;
    const file_name = body.file_name

    const YoloResult = (callback)=>{
        const options = {
            method: 'POST',
            uri: "http://127.0.0.1:5000/test",
            qs: {
                file_name: file_name
            }
        }

        request(options, function (err, res, body) {
            callback(undefined, {
                result:body
            });
        });
    }

    YoloResult((err, {result}={})=>{
        if(err){
            console.log("error!!!!");
            res.send({
                message: "fail",
                status: "fail"
            });
        }
        let json = JSON.parse(result);
        res.send({
            message: "from flask",
            status: "success",
            data:{
                json
            }
        });
    })

});

module.exports = router;