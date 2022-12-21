import sqlite3
import json
from tqdm.auto import tqdm

class SQLiteJSON:
    def __init__(self, dbName: str, TABLE="docs", BODY="body", create_table=True):
        assert sqlite3.sqlite_version_info >= (3,38), "require sqlite >= 3.38"
        self.connector = sqlite3.connect(dbName)
        self.TABLE = TABLE
        self.BODY = BODY
        if create_table:
            self.create_table()

    def create_table(self):
        CREATE_TABLE = f"""
        CREATE TABLE IF NOT EXISTS [{self.TABLE}] (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {self.BODY} JSON
        );
        """
        self.connector.execute(CREATE_TABLE)
        self.connector.commit()

    def _one_tuple_gen(self, data):
        for d in data:
            if type(d) == dict:
                yield (json.dumps(d, ensure_ascii=False),)
            else:
                yield (d,)

    def write_json(self, items: list, batch=1000, disable_progress=False):
        INSERT_RECORD = f"""INSERT INTO [{self.TABLE}] ({self.BODY}) VALUES (?);"""
        cur = self.connector.cursor()
        pbar = tqdm(total=len(items), disable=disable_progress)
        for i in range(0, len(items), batch):
            data = items[i:i+batch]
            cur.executemany(INSERT_RECORD, self._one_tuple_gen(data))
            self.connector.commit()
            pbar.update(len(data))
        cur.close()
        pbar.close()

    def query(self, sql):
        cur = self.connector.execute(sql)
        col = [tuple(x[0] for x in cur.description)]
        data = cur.fetchall()
        cur.close()
        return col + data

    def size(self):
        sql = f"select count(id) from {self.TABLE}"
        return self.connector.execute(sql).fetchone()[0]

    def close(self):
        self.connector.close()
