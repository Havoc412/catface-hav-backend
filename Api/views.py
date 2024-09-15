from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from Api.models import catInforGroup, CatInforSelectMode
from DB import SQLiteDB

# Create your views here.
def link_test(request):
    data = {
        "status": 200,
        "msg": "Linked!"
    }
    return JsonResponse(data)

@require_GET
def search_sql(request):
    """ 读取 sqlite，前端展示所有数据。 """
    # get data
    cat_infor = []
    with SQLiteDB() as db:
        cig = catInforGroup(db)
        rets = cig.select(mode=CatInforSelectMode.BASIC)
        del cig

        if rets is not None:
            for ret in rets:
                infor = {
                    "id": ret._id,
                    "name": ret._name,
                    "breed": ret._breed,
                    "gender": ret._gender,
                }
                cat_infor.append(infor)
    # return data
    data = {
        "status": 200,
        "cat_infor_list": cat_infor
    }
    return JsonResponse(data)

@require_POST
def filter_by_poi(request):
    """
    借助上传的 POI 信息 和 cats_id，过滤掉一部分初筛后的目标
    :param request: {
        'POI': {
            log: xxx,
            lat: xxx
        }, 使用者实时上传的点位。
        'cats_id': int[]
    }
    :return:
    """
    # get params
    poi_human = request.POST.get('POI')
    cats_id = request.POST.get("cats_id")

    # search and filter











