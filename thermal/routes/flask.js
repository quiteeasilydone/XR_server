const express = require('express');
const axios = require('axios');

const router = express.Router();

const response_list = {result : false, responses : []}

router.post('/', (req, res) => {
    try{
        let body = req.body;
        const img_id = body.id;
        const palettemode = body.palettemode;
        const option = body.option;

        const flaskServerUrl = 'http://127.0.0.1:5001/flir';

        img_id.forEach( async(value, index, img_id) => {
            console.log(value)
            const response = await axios.post(flaskServerUrl, { id: value, palettemode: palettemode, option: option }
            );
            console.log(response.data)
            response_list.responses.push(response.data)
        });
        
        response_list.result = true

        res.send(response_list);

    } catch (error) {
        console.error(error);
        res.status(500).send('Error sending data to Flask server: ' + error, response_list);
    }

});

module.exports = router;