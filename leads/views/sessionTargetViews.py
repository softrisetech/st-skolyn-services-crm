from rest_framework import status
from ..models import SessionTarget
from ..serializers import SessionTargetSerializer
from rest_framework.decorators import api_view
from core.utils.pagination_utils import CustomPagination
from core.utils.decorators import access_control_middleware
from core.utils.date_time_converter import DateTimeConverter
from ..utils.filters import filter_by_branches, filter_by_sessions
from core.utils.response_utils import success_response, error_response
from core.utils.helpers import check_if_user_is_staff
from access_control.utils.permission_constants import (
    SESSION_TARGET_BRANCH_WISE
)
from access_control.utils.permission_helpers import (
    view_branch_wise, 
)


def __queryset(data, business_id):
    filters = {"business_id": business_id}
    is_staff = check_if_user_is_staff(data)

    if is_staff in ["true", True]:
        user_id = data.get('auth_id')
        role_id = data.get('auth_role_id')
        have_branch_wise_permission = view_branch_wise(user_id, role_id, SESSION_TARGET_BRANCH_WISE)
        queryset = SessionTarget.objects.filter(**filters)

        if have_branch_wise_permission:
            branch_id = data.get("auth_branch_id")
            queryset = queryset.filter(branch_id=branch_id)

        return queryset

    return SessionTarget.objects.filter(**filters)


def __apply_filters(queryset, filters):
    queryset = filter_by_branches(queryset, filters)
    queryset = filter_by_sessions(queryset, filters)
    return queryset


@api_view(['POST'])
@access_control_middleware
def get_lead_session_targets(request):
    data = request.data
    timezone = data.get("auth_timezone")
    business_id = data.get('auth_business_id')
    queryset = __queryset(data, business_id)
    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = SessionTargetSerializer(paginated_queryset, many=True).data
    for data in serialized_data:
        data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
        data["updated_at"] = DateTimeConverter.from_utc_datetime(data["updated_at"], timezone)
    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)


@api_view(['POST'])
@access_control_middleware
def get_lead_session_target(request, pk=None):
    data = request.data
    timezone = data.get("auth_timezone")
    business_id = data.get('auth_business_id')
    session_target = __queryset(data, business_id).filter(id=pk).first()
    if not session_target:
        return error_response('session_target_not_found', status.HTTP_404_NOT_FOUND)

    serialized_data = SessionTargetSerializer(session_target).data
    serialized_data["created_at"] = DateTimeConverter.from_utc_datetime(serialized_data["created_at"], timezone)
    serialized_data["updated_at"] = DateTimeConverter.from_utc_datetime(serialized_data["updated_at"], timezone)
    return success_response('record_fetched', status.HTTP_200_OK, serialized_data)


@api_view(['POST'])
@access_control_middleware
def store_lead_session_target(request):
    data = request.data.copy()
    data['business_id'] = data.get('auth_business_id')
    serializer = SessionTargetSerializer(data=data)
    if not serializer.is_valid():
        return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    serializer.save()
    return success_response('record_stored', status.HTTP_201_CREATED, serializer.data)

@api_view(['POST'])
@access_control_middleware
def update_lead_session_target(request, pk=None):
    data = request.data.copy()
    business_id = data.get('auth_business_id')
    session_target = __queryset(data, business_id).filter(id=pk).first()
    if not session_target:
        return error_response('session_target_not_found', status.HTTP_404_NOT_FOUND)

    data['business_id'] = business_id
    serializer = SessionTargetSerializer(instance=session_target, data=data, partial=False)
    if not serializer.is_valid():
        return error_response('record_updation_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    serializer.save()
    return success_response('record_updated', status.HTTP_200_OK, serializer.data)


@api_view(['POST'])
@access_control_middleware
def delete_lead_session_target(request, pk=None):
    data = request.data
    business_id = data.get('auth_business_id')
    session_target = __queryset(data, business_id).filter(id=pk).first()
    if not session_target:
        return error_response('session_target_not_found', status.HTTP_404_NOT_FOUND)

    session_target.delete()
    return success_response('record_deleted', status.HTTP_200_OK)
