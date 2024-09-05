from django.shortcuts import render
from django.http import JsonResponse

from DB import SQLiteDB

# Create your views here.
def link_test(request):
    data = {
        "status": 200,
        "msg": "Linked!"
    }
    return JsonResponse(data)


def search_sql(request):
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
