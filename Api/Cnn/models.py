import json
from enum import Enum
from typing import List

from django.db import models

from DB import MySQL

from utils.utils import trans_breedEn_to_idx

# # 准备弃用
# class AnmFaceBreed:# (models.Model):
#     Top1 = models.PositiveSmallIntegerField(verbose_name="Top1")
#     Prob1 = models.FloatField(verbose_name="概率1")
#     Top2 = models.PositiveSmallIntegerField(verbose_name="Top2")
#     Prob2 = models.FloatField(verbose_name="概率2")
#     Top3 = models.PositiveSmallIntegerField(verbose_name="Top3")
#     Prob3 = models.FloatField(verbose_name="概率3")
#
#     AnimalId = models.IntegerField(verbose_name="动物ID")
#
#     _attrs = ['Top1', 'Prob1', 'Top2', 'Prob2', 'Top3', 'Prob3', 'AnimalId']
#     _table_name = "Api_anmfacebreed"
#
#     def __init__(self, **kwargs):
#         """
#         :param kwargs: 采取字典的输入形式
#         """
#         # 基本属性
#         self._id = kwargs.get('id', None)
#         self._top1 = kwargs.get('Top1', None)
#         self._prob1 = kwargs.get('Prob1', None)
#         self._top2 = kwargs.get('Top2', None)
#         self._prob2 = kwargs.get('Prob2', None)
#         self._top3 = kwargs.get('Top3', None)
#         self._prob3 = kwargs.get('Prob3', None)
#         self._animal_id = kwargs.get('AnimalId', None)  # important
#
#         # 检查是否存在未知的额外参数，增加灵活性
#         for key, value in kwargs.items():
#             if not hasattr(self, f'_{key}'):
#                 setattr(self, f'_{key}', value)
#
#     def setProbsMap(self):
#         """
#         将 topX 和 probX 属性整合成一个字典返回。
#         每个元素是一个键值对 (topX: probX)。
#         """
#         result = {}  # 使用字典初始化
#         for i in range(1, 4):  # 假设最多有3个结果
#             try:
#                 top_attr = getattr(self, f'_top{i}')
#                 prob_attr = getattr(self, f'_prob{i}')
#                 if top_attr is not None and prob_attr is not None:
#                     result[top_attr] = prob_attr
#             except AttributeError as e:
#                 print(f"Warning: Failed to get attribute: {e}")
#         return result
#
#     def calTargetFaceBreedProb(self, target_breeds) -> float:
#         """
#         计算目标 breeds 在当前结果中出现的概率。
#         :param target_breeds: 目标 breeds，{
#             'top5': [], 'conf': []
#         }
#         :return: 目标 breeds 在当前结果中出现的概率。
#         """
#         probs_map = self.setProbsMap()
#         sum_prob = 0
#         for breed, conf in zip(target_breeds['top5'], target_breeds['conf']):
#             sum_prob += probs_map.get(trans_breedEn_to_idx(breed), 0) * conf
#         return sum_prob
#
#     def calTargetFaceBreedProbWithID(self, target_breeds):
#         return {
#             'id': self._id,  # TODO 这里的 ID 还不是 animal_id.
#             'conf': self.calTargetFaceBreedProb(target_breeds)
#         }
#
# class AnmFaceBreedGroup:
#     _table_name = "anm_face_breeds"
#     _attrs = ['id', 'Top1', 'Prob1', 'Top2', 'Prob2', 'Top3', 'Prob3']
#     def __init__(self, db: MySQL):
#         self._db = db
#         self._anmFaceBreedList = []
#
#     def init(self, animal_ids):
#         """
#         初始化
#         :param animal_id: 动物 ID
#         :return: None
#         """
#         self._anmFaceBreedList = []
#         if animal_ids is not None and not isinstance(animal_ids, list):
#             animal_ids = list(animal_ids)
#         return animal_ids
#
#     def select(self, animal_ids=None) -> List[AnmFaceBreed]:
#         animal_ids = self.init(animal_ids)
#
#         # create query
#         attrs = ', '.join(self._attrs)
#         query = f"SELECT {attrs} FROM {self._table_name}"
#
#         if animal_ids:
#             query += f" WHERE animal_id IN ({','.join(['%s'] * len(animal_ids))})"
#
#         # exe
#         res = self._db.execute_query(query, animal_ids)
#
#         # load data
#         if res is None:
#             return None
#         for row in res:
#             self._anmFaceBreedList.append(AnmFaceBreed(**row))
#
#         return self._anmFaceBreedList
#
# if __name__ == "__main__":
#     kwargs = {
#         'id': 1,
#         'Top1': 'Breed1',
#         'Prob1': 0.9,
#         'Top2': 'Breed2',
#         'Prob2': 0.8,
#         'Top3': 'Breed3',
#         'Prob3': 0.7,
#         'AnimalId': 'A123'
#     }
#     breed = AnmFaceBreed(**kwargs)
#
#     print(breed.getTopX())

