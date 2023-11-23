const https = require('https');
const fs = require('fs');
const express = require('express');
const app = express();
const port = 8080;
const path = require('path');

const keyPath = path.join('./key.pem');
const certPath = path.join('./cert.pem');

const analyze = require('./routes/flask.js');

const test10 = require('./routes/dbConnection.js');

https.createServer(
    {key: fs.readFileSync(keyPath),
    cert: fs.readFileSync(certPath)},

    app.use(express.json()),

    // app.get('/', (req, res) => {
    // res.json({
    // success: true,
    // });
    // });
    
    
    app.use("/analyze", analyze),
    
    
    app.use("/dbConnection", test10),
    
    // const acquireData = require('./routes/acquireData.js');
    // app.use("/acquireData", acquireData)
    
    app.use('/', (req, res) => {
        res.send('connect');
        console.log(`server is listening at localhost:${port}`);
    })
).listen(port)
