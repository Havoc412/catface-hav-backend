import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from Api.models import catInforGroup, CatInforSelectMode
from DB import SQLiteDB
from .utils import haversine_2

# Create your views here.
def link_test(request):
    data = {
        "status": 200,
        "msg": "Linked!"
    }
    return JsonResponse(data)

# @require_GET
# def search_sql(request):
#     """ 读取 sqlite，前端展示所有数据。 """
#     # get data
#     cat_infor = []
#     with SQLiteDB() as db:
#         cig = catInforGroup(db)
#         rets = cig.select(mode=CatInforSelectMode.BASIC)
#         del cig
#
#         if rets is not None:
#             for ret in rets:
#                 infor = {
#                     "id": ret._id,
#                     "name": ret._name,
#                     "breed": ret._breed,
#                     "gender": ret._gender,
#                 }
#                 cat_infor.append(infor)
#     # return data
#     data = {
#         "status": 200,
#         "cat_infor_list": cat_infor
#     }
#     return JsonResponse(data)

@require_POST
def filter_by_poi(request):
    """
    借助上传的 POI 信息 和 cats_id，过滤掉一部分初筛后的目标
    :param request: {
        'poi': {
            log: xxx,
            lat: xxx
        }, 使用者实时上传的点位。
        'cats_id': int[]
    }
    :return: cats_id: int[] 然后前端过滤掉不存在者。
    """
    # get params
    data = json.loads(request.body.decode('utf-8'))
    poi_human = data.get('poi')
    cats_id = data.get("cats_id")

    poi_human = (poi_human['lat'], poi_human['lon'])  # trans

    # search and filter
    with SQLiteDB() as db:
        cig = catInforGroup(db)
        cig.select(cats_id=cats_id, mode=CatInforSelectMode.POI)

        for catinfor in cig._catInforList:
            poi_cat = (catinfor._latitude, catinfor._longitude)

            if haversine_2(poi_human, poi_cat) >= catinfor._activity_radius:
                print(haversine_2(poi_human, poi_cat))
                cats_id.remove(catinfor._id)

    data = {
        "status": 200,
        "cats_id": cats_id
    }
    return JsonResponse(data)












