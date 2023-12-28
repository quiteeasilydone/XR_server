const fs = require('fs');
const express = require('express');
const app = express();
const port = 8081;
const path = require('path');

const checkImg = require('./routes/checkImg.js');
const saveImg = require('./routes/saveImg.js');
const flask = require('./routes/flask.js');

// const test10 = require('./routes/dbConnection.js');

app.use(express.json()),

app.use("/checkimg", checkImg)
app.use("/saveimg", saveImg)
app.use("/flask", flask)

app.use('/', (req, res) => {
    res.send('connect');
    console.log(`server is listening at localhost:${port}`);
    }).listen(port)
