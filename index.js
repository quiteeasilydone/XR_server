const express = require('express');
const app = express();
const port = 8080;
app.use(express.json())

// app.get('/', (req, res) => {
// res.json({
// success: true,
// });
// });

const fourier = require('./routes/flask.js');
app.use("/fourier", fourier)

const test10 = require('./routes/dbConnection.js');
app.use("/dbConnection", test10)

const acquireData = require('./routes/acquireData.js');
app.use("/acquireData", acquireData)

app.listen(port, () => {
console.log(`server is listening at localhost:${port}`);
});
