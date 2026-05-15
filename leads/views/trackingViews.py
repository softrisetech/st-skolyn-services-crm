from django.db.models import Q
from rest_framework import status
from ..models import Tracking, Lead
from ..serializers import TrackingSerializer
from rest_framework.decorators import api_view
from core.utils.pagination_utils import CustomPagination
from core.utils.decorators import access_control_middleware
from core.utils.date_time_converter import DateTimeConverter
from core.utils.response_utils import success_response, error_response

def __queryset(business_id, lead_id):
    return Tracking.objects.filter(business_id=business_id, lead_id=lead_id)


def __apply_filters(queryset, filters):
    search_query = filters.get('search')
    if search_query:
        queryset = queryset.filter(
            Q(model_type__icontains=search_query)
        )
        
    return queryset.order_by('-created_at')


@api_view(['POST'])
@access_control_middleware
def get_lead_trackings(request, lead_id):
    data = request.data
    timezone = data.get("auth_timezone")
    business_id = data.get('auth_business_id')

    lead = Lead.objects.filter(id=lead_id, business_id=business_id).first()
    if not lead:
        return error_response('lead_not_found', status.HTTP_404_NOT_FOUND)
    
    queryset = __queryset(business_id, lead_id)
    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = TrackingSerializer(paginated_queryset, many=True).data
    for data in serialized_data:
        data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)
