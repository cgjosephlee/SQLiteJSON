import sqlite3
try:
    import ujson as json
except ImportError:
    import json
import random
from tqdm.auto import tqdm
from typing import Any

class SQLiteJSON:
    def __init__(self, dbName: str, TABLE: str="docs", BODY: str="body", create_table: bool=True, enable_ext: bool=True):
        """
        Use SQLite as a lightweight NoSQL database.

        Args:
            dbName: database path.
            TABLE: table name.
            BODY: column name.
            create_table: create table if not existed.
            enable_ext: enable extended functions.
        """
        assert sqlite3.sqlite_version_info >= (3,38), "require sqlite >= 3.38"
        self.connector = sqlite3.connect(dbName)
        self.TABLE = TABLE
        self.BODY = BODY
        if create_table:
            self.create_table()
        if enable_ext:
            _SQLiteJSONExt.register(self.connector)

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

    def query(self, sql, header=True):
        """
        Args:
            sql: sql query.
            header: include column name.
        """
        cur = self.connector.execute(sql)
        col = [tuple(x[0] for x in cur.description)]
        data = cur.fetchall()
        cur.close()
        if header:
            return col + data
        else:
            return data

    def size(self):
        sql = f"select count(id) from {self.TABLE}"
        return self.connector.execute(sql).fetchone()[0]

    def close(self):
        self.connector.close()


class _SQLiteJSONExt:
    @staticmethod
    def _registered_funcs():
        # [name, num_params]
        f = [
            ["json_array_contains", 2],
            ["json_array_dropdup", 1],
            ["json_array_randelem", 1]
        ]
        return f

    @classmethod
    def register(cls, conn):
        funcs = cls._registered_funcs()
        for name, num_params in funcs:
            conn.create_function(name, num_params, getattr(cls, name))

    @staticmethod
    def json_array_contains(arr: str, value: Any) -> bool:
        return value in json.loads(arr)

    @staticmethod
    def json_array_dropdup(arr: str) -> str:
        # Order not preserved
        return json.dumps(list(set(json.loads(arr))))

    @staticmethod
    def json_array_randelem(arr: str) -> Any:
        a = json.loads(arr)
        return a[random.randrange(len(a))]
