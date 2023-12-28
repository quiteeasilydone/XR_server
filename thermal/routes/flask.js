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

        const flaskServerUrl = 'http://127.0.0.1:5000/flir';

        img_id.forEach( async(value, index, img_id) => {
            const response = await axios.post(flaskServerUrl, {
                params: { id: value, palettemode: palettemode, option: option }
            });
            console.log(response)
            response_list.responses.push(response)
        });
        
        response_list.result = true

        res.send(response_list);

    } catch (error) {
        console.error(error);
        res.status(500).send('Error sending data to Flask server: ' + error, response_list);
    }

});

module.exports = router;