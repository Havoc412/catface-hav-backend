import os
import pymysql

class MySQLDB:
    # INFO DesignIDEA 只做对一些常用基础功能的封装，其他都直接采用手写 SQL 的方式实现。
    def __init__(self, host="localhost", user="root", password="havocantelope412", database=""):
        """
        初始化连接到 MySQL 数据库的类;
        这里函数接收参数的设定主要是方便单元测试；
        """
        self.host = os.getenv("MYSQL_HOST", host)
        self.user = os.getenv("MYSQL_USER", user)
        self.password = os.getenv("MYSQL_PASSWORD", password)
        self.database = os.getenv("MYSQL_DATABASE", database)
        self.conn = None

        self.connect()

    def connect(self):
        # check 'None'
        assert self.host and self.user and self.password and self.database, "参数设置不正确，请检查！"
        """ 创建一个数据库连接到 MySQL 数据库 """
        try:
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("Connection established to database.")
        except pymysql.MySQLError as e:
            print(e)

    def execute_query(self, query, params=None):
        """ 执行 SQL 查询并返回结果 """
        try:
            with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                return results
        except pymysql.MySQLError as e:
            print(f"❌ Err: Query [{query}]", e)

    def fetch_all(self, table_name="animals"):
        """ 查询全表信息 """
        query = f"SELECT * FROM {table_name}"
        return self.execute_query(query)

    def insert(self, query, params=None):
        """
        插入一条数据，同时返回 对应的 id。
        :return:
        """
        try:
            with self.conn.cursor() as cursor:
                # 执行插入操作
                cursor.execute(query, params or ())
                self.conn.commit()  # 提交事务
                # 获取最后插入的 ID
                last_row_id = cursor.lastrowid
                return last_row_id  # 返回 ID
        except pymysql.MySQLError as e:
            self.conn.rollback()  # 回滚事务
            print(f"❌ 数据插入出错: {e}, {query}", params)
            return None

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
    # INFO Way1 方式一
    db = MySQLDB(database="catface")

    # 示例查询
    query = "SELECT * FROM anm_face_breeds WHERE id IN (%s)"
    params = (1)
    res = db.execute_query(query, params)
    print(res)

    # # INFO Way2 使用上下文管理器
    # with MySQLDB(database="catface") as db:
    #     results = db.fetch_all()
    #     print(results)
