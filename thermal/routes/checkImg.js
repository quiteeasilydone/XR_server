const express = require('express')
const fs = require('fs')
const path = require('path')

const router = express.Router()

function check_img_list(id, id_list){
    const img_path = path.join(".", "imgs", "thermal", id)
    if (fs.existsSync(img_path)){
        console.log("exists!")
    } else {
        console.log("not exists!")
        id_list.push(id)
    }
}

router.post('/', (req, res) => {
    try{
        const response = {"result" : false, "id" : null, "hasall" : false }
        let body = req.body
        const img_ids = body.id
        const id_list = []

        for (const id of img_ids){
            check_img_list(id, id_list)
        }

        console.log(id_list)
        response.id = id_list

        if (id_list.length === 0 ){
            response.hasall = true
        }

        response.result = true
        res.send(response)

    } catch (error) {
        console.error(error)
        res.status(500).send('Error sending data to Flask server: ' + error, response)
    }
})

module.exports = router