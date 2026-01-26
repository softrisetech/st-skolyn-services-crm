from ..models import Tracking
from rest_framework import status
from ..serializers import TrackingSerializer
from rest_framework.decorators import APIView
from django.utils.decorators import method_decorator
from core.utils.pagination_utils import CustomPagination
from core.utils.decorators import access_control_middleware
from core.utils.date_time_converter import DateTimeConverter
from ..utils.filters import filter_by_type, filter_by_model_type
from core.utils.response_utils import success_response, error_response

class TrackingView(APIView):
    pagination_class = CustomPagination

    def get_queryset(self, business_id):
        return Tracking.objects.filter(business_id=business_id)

    def apply_filters(self, queryset, filters):
        lead_id = filters.get('lead_id')
        if lead_id is not None:
            queryset = queryset.filter(lead_id=lead_id)

        queryset = filter_by_type(queryset, filters)
        queryset = filter_by_model_type(queryset, filters)

        return queryset.order_by('-created_at')

    @method_decorator(access_control_middleware)
    def get(self, request, pk=None):
        data = request.query_params
        timezone = data.get("auth_timezone")
        business_id = data.get('auth_business_id')
        queryset = self.get_queryset(business_id)

        if pk:
            tracking = queryset.filter(id=pk).first()
            if tracking:
                serialized_data = TrackingSerializer(tracking).data
                serialized_data["created_at"] = DateTimeConverter.from_utc_datetime(serialized_data["created_at"], timezone)
                return success_response('record_fetched', status.HTTP_200_OK, serialized_data)
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

        # List view with pagination and filters
        filters = data
        queryset = self.apply_filters(queryset, filters)
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serialized_data = TrackingSerializer(paginated_queryset, many=True).data
        for data in serialized_data:
            data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
        response_data = paginator.get_paginated_response(serialized_data)
        return success_response('record_fetched', status.HTTP_200_OK, response_data)

    @method_decorator(access_control_middleware)
    def post(self, request):
        data = request.data.copy()
        data['business_id'] = request.data.get('auth_business_id')
        serializer = TrackingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return success_response('record_stored', status.HTTP_201_CREATED, serializer.data)
        return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    @method_decorator(access_control_middleware)
    def delete(self, request, pk=None):
        business_id = request.data.get('auth_business_id')
        try:
            tracking = Tracking.objects.get(id=pk, business_id=business_id)
            tracking.delete()
            return success_response('record_deleted', status.HTTP_200_OK)
        except Tracking.DoesNotExist:
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)
