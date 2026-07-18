const sqlite3 = require('sqlite3');
const { promisify } = require('node:util');

// Envolve o driver de callbacks do sqlite3 numa API de promises,
// permitindo async/await em models e services.
function openDatabase(path) {
    const db = new sqlite3.Database(path);
    return {
        get: promisify(db.get.bind(db)),
        all: promisify(db.all.bind(db)),
        exec: promisify(db.exec.bind(db)),
        close: promisify(db.close.bind(db)),
        run(sql, params = []) {
            return new Promise((resolve, reject) => {
                db.run(sql, params, function (err) {
                    if (err) return reject(err);
                    resolve({ lastID: this.lastID, changes: this.changes });
                });
            });
        }
    };
}

module.exports = { openDatabase };
