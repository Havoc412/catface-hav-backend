import json

from django.http import JsonResponse

from .utils import haversine_2

# Create your views here.
def link_test(request):
    data = {
        "status": 200,
        "msg": "Linked!"
    }
    return JsonResponse(data)
