var mysql      = require('mysql');
var connection = mysql.createConnection({
  host     : 'localhost',
  user     : 'xr_user',
  password : 'inhahci',
  database : 'xr_db'
});
 
connection.connect();
 
module.exports = connection;