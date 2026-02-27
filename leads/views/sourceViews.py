from django.db.models import Q
from rest_framework import status
from ..models import Source, Lead
from ..serializers import SourceSerializer
from rest_framework.decorators import api_view
from ..utils.lead_utils import encrypt_business_id
from core.utils.pagination_utils import CustomPagination
from core.utils.helpers import has_active_child_references
from core.utils.decorators import access_control_middleware
from core.utils.date_time_converter import DateTimeConverter
from ..utils.filters import filter_by_active, filter_by_sort_order
from core.utils.response_utils import success_response, error_response


def __queryset(business_id):
    return Source.objects.filter(business_id=business_id)


def __apply_filters(queryset, filters):
    search_query = filters.get('search')
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) | 
            Q(slug__icontains=search_query) |
            Q(description__icontains=search_query) 
        )

    queryset = filter_by_active(queryset, filters)
    queryset = filter_by_sort_order(queryset, filters)
    return queryset


@api_view(['POST'])
@access_control_middleware
def get_lead_sources(request):
    data = request.data
    timezone = data.get("auth_timezone")
    business_id = data.get('auth_business_id')
    queryset = __queryset(business_id)
    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = SourceSerializer(paginated_queryset, many=True).data
    for data in serialized_data:
        data["encrypted_business_id"] = encrypt_business_id(business_id)
        data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
        data["updated_at"] = DateTimeConverter.from_utc_datetime(data["updated_at"], timezone)
    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)


@api_view(['POST'])
@access_control_middleware
def get_lead_source(request, pk=None):
    data = request.data
    timezone = data.get("auth_timezone")
    business_id = data.get('auth_business_id')
    source = __queryset(business_id).filter(id=pk).first()
    if not source:
        return error_response('source_not_found', status.HTTP_404_NOT_FOUND)

    serialized_data = SourceSerializer(source).data
    serialized_data["encrypted_business_id"] = encrypt_business_id(business_id)
    serialized_data["created_at"] = DateTimeConverter.from_utc_datetime(serialized_data["created_at"], timezone)
    serialized_data["updated_at"] = DateTimeConverter.from_utc_datetime(serialized_data["updated_at"], timezone)
    return success_response('record_fetched', status.HTTP_200_OK, serialized_data)


@api_view(['POST'])
@access_control_middleware
def store_lead_source(request):
    data = request.data.copy()
    data['business_id'] = data.get('auth_business_id')
    serializer = SourceSerializer(data=data)
    if not serializer.is_valid():
        return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    serializer.save()
    return success_response('record_stored', status.HTTP_201_CREATED, serializer.data)

@api_view(['POST'])
@access_control_middleware
def update_lead_source(request, pk=None):
    data = request.data.copy()
    business_id = data.get('auth_business_id')
    source = __queryset(business_id).filter(id=pk).first()
    if not source:
        return error_response('source_not_found', status.HTTP_404_NOT_FOUND)

    data['business_id'] = business_id
    serializer = SourceSerializer(instance=source, data=data, partial=False)
    if not serializer.is_valid():
        return error_response('record_updation_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    serializer.save()
    return success_response('record_updated', status.HTTP_200_OK, serializer.data)


@api_view(['POST'])
@access_control_middleware
def delete_lead_source(request, pk=None):
    business_id = request.data.get('auth_business_id')
    source = __queryset(business_id).filter(id=pk).first()
    if not source:
        return error_response('source_not_found', status.HTTP_404_NOT_FOUND)

    child_references = [
        {'model': Lead, 'foreign_key': 'source_id'}
    ]
    has_refs = has_active_child_references(child_references, pk, business_id)
    if has_refs:
        return error_response("related_source_record_found_on_deletion", status.HTTP_400_BAD_REQUEST)

    source.delete()
    return success_response('record_deleted', status.HTTP_200_OK)
