# SQLiteJSON
Use SQLite as a lightweight NoSQL database to store json documents.

# Example
- [SQLite JSON functions](https://www.sqlite.org/json1.html)
- [Demo notebook](https://github.com/cgjosephlee/SQLiteJSON/blob/main/tests/demo.ipynb)
```shell
# Installation
pip install git+https://github.com/cgjosephlee/SQLiteJSON
```
```python
import json
from SQLiteJSON import SQLiteJSON

# create a db, or open an existed db
db = SQLiteJSON("pokedex.db")

# write json documents
db.write_json(data)

# query a document
db.query("select body from docs limit 1")

# fitler value
db.query("""select body->>'$.name', body->>'$.spawn_chance' from docs where body->>'$.spawn_chance' < 0.01""")

# group by on values in array
db.query("""select k.value, count(k.value) from docs, json_each(body->>'$.type') k group by k.value order by count(k.value)""")

# filter if array contains a specific value
db.query("""select body from docs, json_each(body->>'$.type') k where k.value = 'Ice'""")

# same as above but with extented function
db.query("""select body from docs where json_array_contains(body->>'$.type', 'Ice')""")
```

# Extended functions
This module also includes a few useful functions.
- `json_array_contains(arr, value)`: check if value in arr.
- `json_array_dropdup(arr)`: drop duplicates.
- `json_array_randelem(arr)`: random element.
