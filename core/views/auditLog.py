from rest_framework.decorators import api_view
from rest_framework import status
from core.audit_models import ActivityLog
from core.auditSerializers import ActivityLogSerializer
from core.utils.response_utils import success_response, error_response
from core.utils.pagination_utils import CustomPagination
from core.utils.decorators import access_control_middleware


def __queryset(business_id):
    return ActivityLog.objects.filter(business_id=business_id)


def __apply_filters(queryset, filters):
    object_id = filters.get('object_id')
    if object_id:
        queryset = queryset.filter(object_id=object_id)

    model_name = filters.get('model_name')
    if model_name:
        queryset = queryset.filter(model_name__icontains=model_name)

    action = filters.get('action')
    if action:
        queryset = queryset.filter(action=action)

    auth_ids = filters.get('auth_id')
    if auth_ids:
        if isinstance(auth_ids, str):
            auth_ids = [aid.strip() for aid in auth_ids.split(',') if aid.strip()]
        if auth_ids:
            queryset = queryset.filter(auth_id__in=auth_ids)

    business_ids = filters.get('business_id')
    if business_ids:
        if isinstance(business_ids, str):
            business_ids = [bid.strip() for bid in business_ids.split(',') if bid.strip()]
        if business_ids:
            queryset = queryset.filter(business_id__in=business_ids)

    date_from = filters.get('date_from')
    if date_from:
        queryset = queryset.filter(timestamp__date__gte=date_from)

    date_to = filters.get('date_to')
    if date_to:
        queryset = queryset.filter(timestamp__date__lte=date_to)

    remote_addr = filters.get('remote_addr')
    if remote_addr:
        queryset = queryset.filter(remote_addr=remote_addr)

    return queryset


@api_view(['POST'])
@access_control_middleware
def get_activity_logs(request):
    data = request.data
    auth_business_id = data.get('auth_business_id')
    pk = data.get('id')

    queryset = __queryset(auth_business_id)

    # Single record fetch by ActivityLog UUID
    if pk:
        log = queryset.filter(id=pk).first()
        if not log:
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

        return success_response(
            'record_fetched',
            status.HTTP_200_OK,
            ActivityLogSerializer(log).data
        )

    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = ActivityLogSerializer(paginated_queryset, many=True).data
    response_data = paginator.get_paginated_response(serialized_data)

    return success_response('record_fetched', status.HTTP_200_OK, response_data)