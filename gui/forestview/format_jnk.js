const fs = require('fs');

fs.readFile('jnk', (err,data) => {
    obj = JSON.parse(data);
    console.log(JSON.stringify(obj, null, '  '));
})
