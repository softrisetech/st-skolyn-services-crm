from rest_framework import status
from django.urls import path, include
from rest_framework.decorators import api_view
from .utils.response_utils import success_response


@api_view(['POST'])
def health_check(request):
    return success_response("health_ok", status.HTTP_200_OK)

urlpatterns = [
    path('', health_check, name='health_check'),
    path('', include('access_control.urls')),
    path('', include('leads.urls')),
]
