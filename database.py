import sqlite3

class Database:
    def __init__(self,db_name) -> None:
        self.conn = sqlite3.connect(db_name)
        # conn.commit()
        # conn.close()
    
    def getDB(self):
        return self.conn

    def __del__(self):
        # print("析构函数工作")
        self.conn.close()

# db = Database("webDatabase.db")