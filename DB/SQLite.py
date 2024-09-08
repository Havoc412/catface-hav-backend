import sqlite3
from sqlite3 import Error

class SQLiteDB:
    def __init__(self, db_file="./db.sqlite3"):
        """ 初始化连接到 SQLite 数据库的类 """
        self.db_file = db_file
        self.conn = None
        self.connect()

    def connect(self):
        """ 创建一个数据库连接到 SQLite 数据库 """
        try:
            self.conn = sqlite3.connect(self.db_file)
            print("Connection established to database.")
        except Error as e:
            print(e)

    def insert_animal(self, name, kind, sex, breed):
        """
        插入一条数据，同时返回 对应的 id。
        :param name:
        :param kind:
        :param sex:
        :param breed:
        :return:
        """
        cursor = self.conn.cursor()

        # 插入数据的 SQL 语句
        sql = 'INSERT INTO Api_catinfor (name, kind, sex, breed) VALUES (?, ?, ?, ?)'

        try:
            # 执行插入操作
            cursor.execute(sql, (name, kind, sex, breed))
            self.conn.commit()  # 提交事务
            # 获取最后插入的 ID
            last_row_id = cursor.lastrowid
            return last_row_id  # 返回 ID
        except sqlite3.Error as e:
            self.conn.rollback()  # 回滚事务
            print(f"数据插入出错: {e}")
            return None
        finally:
            # 关闭连接
            cursor.close()

    def execute_query(self, query, params=None):
        """ 执行 SQL 查询并返回结果 """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(e)

    def fetch_by_ids(self, id_list):
        """ 查询特定 id 列表的记录 """
        placeholders = ', '.join('?' for _ in id_list)  # 创建参数占位符
        query = f"SELECT * FROM Api_catinfor WHERE id IN ({placeholders})"
        return self.execute_query(query, id_list)

    def fetch_all(self, table_name="Api_catinfor"):
        """ 查询全表信息 """
        query = f"SELECT * FROM {table_name}"
        return self.execute_query(query)

    def close(self):
        """ 关闭数据库连接 """
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def __enter__(self):
        """ 支持上下文管理器进入方法 """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ 支持上下文管理器退出方法 """
        self.close()

if __name__ == "__main__":
    db = SQLiteDB(db_file="../db.sqlite3")
    res = db.fetch_by_ids([1, 2, 3 ,4])
    print(res)

    # cat_infor = []
    # with SQLiteDB(db_file="../db.sqlite3") as db:
    #     results = db.fetch_all()
    #     print(results)
    #     for res in results:
    #         infor = {
    #             "id": res[0],
    #             "name": res[1],
    #             "breed": res[2],
    #             "gender": res[3],
    #             "breed_en": res[4]
    #         }
    #         cat_infor.append(infor)
    # print(cat_infor)
