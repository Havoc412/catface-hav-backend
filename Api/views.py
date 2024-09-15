from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from DB import SQLiteDB

# Create your views here.
def link_test(request):
    data = {
        "status": 200,
        "msg": "Linked!"
    }
    return JsonResponse(data)

def search_sql(request):
    """ 读取 sqlite，前端展示所有数据。 """
    if request.method == 'GET':
        # get data
        cat_infor = []
        with SQLiteDB() as db:
            results = db.fetch_all()
            for res in results:
                infor = {
                    "id": res[0],
                    "name": res[1],
                    "breed": res[2],
                    "gender": res[3]
                }
                cat_infor.append(infor)
        # return data
        data = {
            "status": 200,
            "cat_infor_list": cat_infor
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'status': 200, 'message': 'Invalid request'})

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











