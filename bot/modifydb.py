import sqlite3

class Modifydb:
    SCHEMA = ''' 
            PRAGMA synchronous=FULL;
            
            CREATE TABLE IF NOT EXISTS main (
            id integer NOT NULL UNIQUE,
            url text,
            sent text,
            full text
            ); '''
     
    def __init__(self, db):
        self._db = sqlite3.connect(db, isolation_level=None)
        self._db.executescript(self.SCHEMA)

    def __del__(self):
        self._db.close()

    # adds a row to db
    def insert_data(self, id, url, sent, full):
        self._db.execute('INSERT OR IGNORE INTO main (id, url, sent, full) VALUES (?,?,?,?)', (id,url,sent,full))

  

    # selects pic url that is not sent 
    def select_unsent_pic(self):
        sql = 'SELECT id,url,full FROM main WHERE sent like ? and url not like ? ORDER BY id ASC LIMIT 1'
        return self._db.execute(sql, ('no', '%.mp4',)).fetchone()


    def select_unsent_vid(self):
        sql = 'SELECT id,url,full FROM main WHERE sent like ? and url like ? ORDER BY id ASC LIMIT 1'
        return self._db.execute(sql, ('no', '%.mp4',)).fetchone()

    # modify row as sent    
    def set_sent(self, id):
        sql = 'UPDATE main SET sent = ? WHERE id = ? LIMIT 1'
        self._db.execute(sql, ('yes',id))
        

