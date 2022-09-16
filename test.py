import sqlite3
conn = sqlite3.connect("webDatabase.db")
conn.execute("create table if not exists products(id primary key, name varchar(20))")
conn.commit()
conn.close()