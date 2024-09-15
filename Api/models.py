import json
from enum import Enum

from django.db import models

from DB.SQLite import SQLiteDB
from utils import trans_breed

# Create your models here.
class catInfor(models.Model):
    # DEFAULT: id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name="主名", max_length=10)
    sex = models.CharField(verbose_name="性别", max_length=10)
    breed = models.CharField(verbose_name="花色", max_length=10)
    breed_en = models.CharField(verbose_name="花色_en", max_length=10, default="unknown")
    description = models.CharField(verbose_name="基本介绍", max_length=100, default="")
    # 增加 经纬度（x.xxxxxx 6位浮点数） # todo INFO 默认值先设置为 C4 了.
    activity_radius = models.IntegerField(verbose_name="活动半径（米）", default=100)
    latitude = models.DecimalField(verbose_name="纬度", max_digits=9, decimal_places=6, default=30.533741)
    longitude = models.DecimalField(verbose_name="经度", max_digits=9, decimal_places=6, default=114.361543)

    def __init__(self, **kwargs):
        """

        :param kwargs: 采取字典的输入形式
        """
        # basic
        self._id = kwargs.get('id', None)
        self._name = kwargs.get('name', None)
        self._gender = kwargs.get('sex', None)
        self._breed = kwargs.get('breed', None)
        self._breed_en = kwargs.get('breed_en', None)
        # description
        self._description = kwargs.get('description', None)
        # poi
        self._activity_radius = kwargs.get('activity_radius', None)
        self._latitude = kwargs.get('latitude', None)
        self._longitude = kwargs.get('longitude', None)

        # todo 特殊处理：如果 kind 存在且 breed 未设置，尝试转换 breed


        # 检查是否存在未知的额外参数，增加灵活性
        for key, value in kwargs.items():
            if not hasattr(self, f'_{key}'):
                setattr(self, f'_{key}', value)

        # if isinstance(infor, tuple):
        #     self._id = infor[0]
        #     self._name = infor[1]
        #     self._gender = infor[2]
        #     self._kind = infor[3]
        #     self._breed = infor[4]
        #     self._description = infor[5]
        #     # todo 整合新的数据。
        # elif isinstance(infor, dict):
        #     self._name = infor['name']
        #     self._gender = infor['gender']
        #     self._kind = infor['breed']  # 目前前端是这样写的...
        #     self._breed = trans_breed(self._kind, en_to_cn=False)  # 中文转英文
        #     # todo 增加 add_cat 中的【介绍】部分。
        # else:
        #     raise ValueError("Infor is not supported!")

    def insert_sql(self, db):
        # todo 这里之后应该封装到 model 而不是 db 里。
        self._id = db.insert_animal(self._name, self._kind, self._gender, self._breed)

    def to_dict_with_conf(self, conf=None):
        assert conf is not None
        return {
            "id": self._id,
            "name": self._name,
            "breed": self._breed, # ch
            "gender": self._gender,
            "conf": conf
        }

    def get_infor_for_rag(self):
        # 处理为 str 输出
        return json.dumps({
            "name": self._name,
            "gender": self._gender,
            "breed": self._kind,
            "description": self._description
        }, ensure_ascii=False)

"""
class：维护一个 catinfor 的数组，或其他集群结构。
func：作为媒介交互 SQLite3

ps. 尽可能解耦，不同储存容器中的顺序并不重要；以及，一一对应。
"""
class CatInforSelectMode(Enum):
    BASIC = ["id", "name", "sex", "breed", "breed_en"]
    POI = ["id", "longitude", "latitude", "activity_radius"]

class catInforGroup:
    _table_name = "Api_catinfor"
    def __init__(self, db: SQLiteDB = None):
        assert db is not None
        self._db = db
        self._catInforList = []
        self._attrs = None

    def init(self, cats_id, mode):
        """
        查询前的初始化：1. 清空 List; 2. 获取 mode 参数; 3. 检查 cats_id.
        :param cats_id:
        :return:
        """
        self._catInforList = []
        self._attrs = mode.value
        if not isinstance(cats_id, list):
            cats_id = list(cats_id)
        return cats_id

    def tuple_to_dict(self, res):
        """ 将 SQLite 返回的 tuple 转换为 dict 格式 """
        return {attr: val for attr, val in zip(self._attrs, res)}

    def select(self, cats_id, mode: CatInforSelectMode=CatInforSelectMode.BASIC):
        """
        目前的版本是 根据 cats_id 主键来查询。
        :param cats_id:
        :param mode:
        :return:
        """
        # init
        cats_id = self.init(cats_id, mode)

        # create query
        attrs = ', '.join(self._attrs)
        placeholders = ', '.join('?' for _ in cats_id)  # 创建参数占位符
        query = f"SELECT {attrs} FROM {self._table_name} WHERE id IN ({placeholders})"

        # exe serch
        results = self._db.execute_query(query, cats_id)

        # load in List
        if results is None:
            return None
        for res in results:
            catinfor = catInfor(**self.tuple_to_dict(res))  # tip 注意解包
            self._catInforList.append(catinfor)

        # ret：use or not
        return self._catInforList










