from django.db import models
from utils import trans_breed

# Create your models here.
class catInfor(models.Model):
    name = models.CharField(verbose_name="主名", max_length=10)
    sex = models.CharField(verbose_name="性别", max_length=10)
    kind = models.CharField(verbose_name="花色", max_length=10)
    breed = models.CharField(verbose_name="花色_en", max_length=10, default="unknown")

    def __init__(self, infor):
        """

        :param infor: 从 SQL 获取的元组
        :return:
        """
        if isinstance(infor, tuple):
            self._id = infor[0]
            self._name = infor[1]
            self._gender = infor[2]
            self._kind = infor[3]
            self._breed = infor[4]
        elif isinstance(infor, dict):
            self._name = infor['name']
            self._gender = infor['gender']
            self._kind = infor['breed']  # 目前前端是这样写的...
            self._breed = trans_breed(self._kind, en_to_cn=False)  # 中文转英文
        else:
            raise ValueError("Infor is not supported!")

    def to_dict_with_conf(self, conf=None):
        assert conf is not None
        return {
            "id": self._id,
            "name": self._name,
            "breed": self._kind,
            "gender": self._gender,
            "conf": conf
        }

    def insert_sql(self, db):
        self._id = db.insert_animal(self._name, self._kind, self._gender, self._breed)
