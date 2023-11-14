const express = require("express");
const router = express.Router(); // API설정을 위한 router 생성

router.post("/", async(req,res) => {
    const qrInfo = req.body.name

    let result_msg = {
        "success": false,
        "errmsg": ""
    }

    result_msg.errmsg = qrInfo

    res.send(result_msg)
}) // post 방식 정의

router.get("/", async(req,res) => {

    let result_msg = {
        "success": false,
        "errmsg": ""
    }

    res.send(result_msg)
}) // get 방식 정의

module.exports = router; // main 함수에 router 인식