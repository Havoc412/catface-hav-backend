import json
from enum import Enum

from django.db import models

from DB.SQLite import SQLiteDB
from DB.MySQL import MySQLDB
from utils import trans_breed

# ----------------------- Animal Information ------------------------- #


# Create your models here.
class Animal:
    _attrs = []
    _table_name = "animals"

    def __init__(self, **kwargs):
        """v
        :param kwargs: 采取字典的输入形式
        """
        # basic
        self._id = kwargs.get('id', None)
        self._name = kwargs.get('name', None)
        self._nick_names = kwargs.get('nick_names', None)
        self._gender = kwargs.get('gender', None)
        self._sterilization = kwargs.get('sterilization', None)
        self._status = kwargs.get('status', None)
        self._breed = kwargs.get('breed', None)
        self._description = kwargs.get('description', None)
        # self._birthday = kwargs.get('birthday', None)
        # self._tags = kwargs.get('tags', None)

        # poi
        self._activity_radius = kwargs.get('activity_radius', None)
        self._latitude = kwargs.get('latitude', None)
        self._longitude = kwargs.get('longitude', None)
        # face breed
        self._face_breeds = kwargs.get('face_breeds', None)
        self._face_breed_probs = kwargs.get('face_breed_probs', None)

        # 检查是否存在未知的额外参数，增加灵活性
        for key, value in kwargs.items():
            if not hasattr(self, f'_{key}'):
                setattr(self, f'_{key}', value)

    def get_insert_values(self):
        # todo 之后换一种 更方便的 方式。
        return [self._name, self._gender, self._breed, self._breed_en, self._description,
                self._activity_radius, self._latitude, self._longitude]

    def insert(self, db):
        # # 获取所有属性  # 这种方式有些难把控
        # attrs = [attr for attr in dir(self) if
        #          attr.startswith('_') and not callable(getattr(self, attr)) and not attr.startswith('__')]
        # attrs = [attr for attr in attrs if attr != '_id']  # 排除 _id 属性
        # attrs = [attr[1:] for attr in attrs]  # 去掉下划线前缀
        #
        # # 构建 SQL 查询
        # placeholders = ', '.join(['?'] * len(attrs))
        # query = f"INSERT INTO {self._table_name} ({', '.join(attrs)}) VALUES ({placeholders})"
        #
        # # 获取属性值
        # values = [getattr(self, f'_{attr}') for attr in attrs]

        # pre
        attrs = ', '.join(self._attrs)
        placeholders = ', '.join('?' for _ in self._attrs)  # 创建参数占位符

        query = f"INSERT INTO {self._table_name} ({attrs}) VALUES ({placeholders})"
        values = self.get_insert_values()

        # 执行插入操作
        self._id = db.insert(query, values)

        print(self._id)

    def getFaceBreedMap(self):
        if self._face_breeds is None or self._face_breed_probs is None:
            return None

        res = {}
        face_breeds = self._face_breeds.split(',')
        face_breed_probs = self._face_breed_probs.split(',')
        for breed, prob in zip(face_breeds, face_breed_probs):
            res[int(breed)] = float(prob)
        return res

    def to_dict_with_conf(self, conf=None):
        """
        Used by Cnn Part
        :param conf:
        :return:
        """
        assert conf is not None
        return {
            "id": self._id,
            "name": self._name,
            "nick_names": self._nick_names,
            "gender": self._gender,
            "breed": self._breed,
            "status": self._status,
            "avatar": self._avatar,
            "latitude": self._latitude,
            "longitude": self._longitude,
            "activity_radius": self._activity_radius,
            "conf": conf
        }

    def get_infor_for_rag(self):
        # 处理为 str 输出
        return json.dumps({
            "name": self._name,
            "gender": self._gender,
            "breed": self._breed,
            "description": self._description
        }, ensure_ascii=False)

    # def to_dict(self, mode=None):

"""
class：维护一个 catinfor 的数组，或其他集群结构。
func：作为媒介交互 SQLite3

ps. 尽可能解耦，不同储存容器中的顺序并不重要；以及，一一对应。
"""
class AnimalSelectMode(Enum):
    BASIC = ["id", "name", "nick_names", "gender", "breed", "status", "avatar",
             "latitude", "longitude", "activity_radius",
             "face_breeds", "face_breed_probs"]
    POI = ["id", "longitude", "latitude", "activity_radius"]
    RAG_BASIC = ["id", "name", "sex", "breed", "descr  iption"]

class AnimalManager:
    _table_name = "animals"
    def __init__(self, db: MySQLDB = None):
        assert db is not None
        self._db = db
        self._animalsList = []
        self._attrs = None

        # link to noticeGroup
        # self._noticeGroup = noticeGroup(self._db)

    def init(self, cats_id, mode):
        """
        查询前的初始化：1. 清空 List; 2. 获取 mode 参数; 3. 检查 cats_id.
        :param cats_id:
        :return:
        """
        self._animalsList = []
        self._attrs = mode.value
        if cats_id is not None and not isinstance(cats_id, list):
            cats_id = list(cats_id)
        return cats_id

    def selectByID(self, cats_id=None, mode: AnimalSelectMode=AnimalSelectMode.BASIC):
        """
        目前的版本是 根据 cats_id 主键来查询。
        :param cats_id: 目标数组；
        :param mode:
        :return:
        """
        # init
        cats_id = self.init(cats_id, mode)

        # create query
        attrs = ', '.join(self._attrs)
        query = f"SELECT {attrs} FROM {self._table_name}"

        # 是否增加 id 的条件查询。
        if cats_id is not None:
            placeholders = ', '.join('%s' for _ in cats_id)  # 创建参数占位符
            query += f" WHERE id IN ({placeholders})"

        # exe serch
        results = self._db.execute_query(query, cats_id)

        # load in List
        if results is None:
            return None
        for res in results:
            aniaml = Animal(**res)  # tip 注意解包
            self._animalsList.append(aniaml)

        # ret：use or not
        return self._animalsList

    def get_name_by_id(self, cat_id):
        """
        根据 cat_id 查询 cat_name  # todo 初步用一个简单的 for，之后再优化。
        :param cat_id:
        :return:
        """
        for catinfor in self._animalsList:
            if catinfor._id == cat_id:
                return catinfor._name
        return "No Name"  # todo 彩蛋()

# ----------------------- Animal Notice ------------------------- #

class notice(models.Model):
    cat_id = models.IntegerField(verbose_name="猫的id")
    content = models.CharField(verbose_name="通知内容", max_length=100)
    human = models.CharField(verbose_name="通知者", max_length=10)
    time = models.DateTimeField(verbose_name="通知时间", auto_now_add=True)
    def __init__(self, **kwargs):
        self._id = kwargs.get('id', None)
        self._cat_id = kwargs.get('cat_id', None)
        self._content = kwargs.get('content', None)
        self._human = kwargs.get('human', None)
        self._time = kwargs.get('time', None)

        # load other attr
        for key, value in kwargs.items():
            if not hasattr(self, f'_{key}'):
                setattr(self, f'_{key}', value)

    def to_dict_with_name(self, name):
        return {
            "id": self._cat_id,
            "content": self._content,
            "human": self._human,
            "time": self._time,
            "name": name
        }

class noticeGroup:
    _table_name = "Api_notice"
    _attrs = ['id', 'cat_id', 'content', 'human', 'time']
    def __init__(self, db):
        self._db = db
        self._noticeList = []

    def init(self, cats_id):
        self._noticeList = []
        if cats_id is not None and not isinstance(cats_id, list):
            cats_id = list(cats_id)
        return cats_id

    def tuple_to_dict(self, res):
        """ 将 SQLite 返回的 tuple 转换为 dict 格式 """
        return {attr: val for attr, val in zip(self._attrs, res)}

    def select(self, cats_id):
        cats_id = self.init(cats_id)

        # query
        attrs = ', '.join(self._attrs)
        query = f"SELECT {attrs} FROM {self._table_name}"

        # 是否增加 id 的条件查询。
        if cats_id is not None:
            placeholders = ', '.join('?' for _ in cats_id)  # 创建参数占位符
            query += f" WHERE cat_id IN ({placeholders})"

        # exe serch
        results = self._db.execute_query(query, cats_id)

        # load in List
        if results is None:
            return None
        for res in results:
            nt = notice(**self.tuple_to_dict(res))  # tip 注意解包
            self._noticeList.append(nt)

        # ret：use or not
        return self._noticeList


