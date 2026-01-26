from django.db.models import Q
from rest_framework import status
from ..models import LostReason, StageReason
from ..utils.filters import filter_by_active
from ..serializers import LostReasonSerializer
from django.utils.decorators import method_decorator
from rest_framework.decorators import APIView, api_view
from core.utils.pagination_utils import CustomPagination
from core.utils.helpers import has_active_child_references
from core.utils.decorators import access_control_middleware
from core.utils.date_time_converter import DateTimeConverter
from core.utils.response_utils import success_response, error_response

class LostReasonView(APIView):
    pagination_class = CustomPagination

    def get_queryset(self, business_id):
        """Retrieve the base queryset filtered by business_id."""
        return LostReason.objects.filter(business_id=business_id)

    def apply_filters(self, queryset, filters):
        """Apply search and filter conditions to the queryset."""
        search_query = filters.get('search')
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query))

        queryset = filter_by_active(queryset, filters)
        return queryset

    @method_decorator(access_control_middleware)
    def get(self, request, pk=None):
        data = request.query_params
        timezone = data.get("auth_timezone")
        business_id = data.get('auth_business_id')
        queryset = self.get_queryset(business_id)

        if pk:
            lost_reason = queryset.filter(id=pk).first()
            if lost_reason:
                serialized_data = LostReasonSerializer(lost_reason).data
                serialized_data["created_at"] = DateTimeConverter.from_utc_datetime(serialized_data["created_at"], timezone)
                serialized_data["updated_at"] = DateTimeConverter.from_utc_datetime(serialized_data["updated_at"], timezone)
                return success_response('record_fetched', status.HTTP_200_OK, serialized_data)
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

        # List view with pagination and filters
        filters = request.query_params
        queryset = self.apply_filters(queryset, filters)
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serialized_data = LostReasonSerializer(paginated_queryset, many=True).data
        for data in serialized_data:
            data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
            data["updated_at"] = DateTimeConverter.from_utc_datetime(data["updated_at"], timezone)
        response_data = paginator.get_paginated_response(serialized_data)
        return success_response('record_fetched', status.HTTP_200_OK, response_data)

    @method_decorator(access_control_middleware)
    def post(self, request):
        data = request.data.copy()
        data['business_id'] = request.data.get('auth_business_id')
        serializer = LostReasonSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return success_response('record_stored', status.HTTP_201_CREATED, serializer.data)
        return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    @method_decorator(access_control_middleware)
    def put(self, request, pk=None):
        data = request.data.copy()
        business_id = data.get('auth_business_id')
        try:
            lost_reason = LostReason.objects.get(id=pk, business_id=business_id)
        except LostReason.DoesNotExist:
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

        data['business_id'] = business_id
        serializer = LostReasonSerializer(instance=lost_reason, data=data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return success_response('record_updated', status.HTTP_200_OK, serializer.data)
        return error_response('record_update_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    @method_decorator(access_control_middleware)
    def delete(self, request, pk=None):
        business_id = request.data.get('auth_business_id')
        try:
            lost_reason = LostReason.objects.get(id=pk, business_id=business_id)
            child_references = [
                {'model': StageReason, 'foreign_key': 'reason_type_id'}
            ]
            has_refs = has_active_child_references(child_references, pk)
            if has_refs:
                return error_response("related_record_delete_failed", status.HTTP_400_BAD_REQUEST)

            lost_reason.delete()
            return success_response('record_deleted', status.HTTP_200_OK)
        except LostReason.DoesNotExist:
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@access_control_middleware
def change_lost_reason_status(request, pk=None):
    data = request.data.copy()
    business_id = request.data.get('auth_business_id')
    try:
        lost_reason = LostReason.objects.get(id=pk, business_id=business_id)
    except LostReason.DoesNotExist:
        return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

    data['business_id'] = business_id
    serializer = LostReasonSerializer(instance=lost_reason, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return success_response('record_updated', status.HTTP_200_OK, serializer.data)
    return error_response('record_update_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)
