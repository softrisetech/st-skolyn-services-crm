from ..models import Tracking
from rest_framework import status
from ..serializers import TrackingSerializer
from rest_framework.decorators import api_view
from core.utils.pagination_utils import CustomPagination
from core.utils.decorators import access_control_middleware
from core.utils.date_time_converter import DateTimeConverter
from ..utils.filters import filter_by_type, filter_by_model_type
from core.utils.response_utils import success_response, error_response

def __queryset(business_id):
    return Tracking.objects.filter(business_id=business_id)


def __apply_filters(queryset, filters):
    lead_id = filters.get('lead_id')
    if lead_id is not None:
        queryset = queryset.filter(lead_id=lead_id)

    return queryset.order_by('-created_at')


@api_view(['POST'])
@access_control_middleware
def get_lead_trackings(request):
    data = request.data
    timezone = data.get("auth_timezone")
    business_id = data.get('auth_business_id')
    queryset = __queryset(business_id)
    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = TrackingSerializer(paginated_queryset, many=True).data
    for data in serialized_data:
        data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)
