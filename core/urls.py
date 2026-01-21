from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework import status
from .utils.response_utils import *


@api_view(['GET'])
def health_check(request):
    return success_response("health_ok", status.HTTP_200_OK)

urlpatterns = [
    path('', health_check, name='health_check'),
]
