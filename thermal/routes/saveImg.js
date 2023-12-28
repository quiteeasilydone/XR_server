const express = require('express')
const axios = require('axios')
const fs = require('fs')
const Buffer = require('buffer').Buffer
const path = require('path')
const multer = require('multer')

const router = express.Router()

function save_img(id, encodeImg){
    const imgPath = path.join(".", "imgs", "thermal", "thermal_" + id + ".jpg")
    const imgDir = path.join(".", "imgs", "thermal");
    if (!fs.existsSync(imgDir)) {
        fs.mkdirSync(imgDir, { recursive: true });
    }
    let decodeImg = Buffer.from(encodeImg, 'base64')
    fs.writeFileSync(imgPath, decodeImg)
}

router.post('/', (req, res) => {
    try{
        let body = req.body
        const img_ids = body.id
        const imgs = body.img

        img_ids.forEach((value, index, img_ids) => {
            save_img(value, imgs[index])
        });

        res.send("save all imgs")

    } catch (error) {
        console.error(error)
        res.status(500).send('Error sending data to Flask server: ' + error)
    }
})

module.exports = router;