from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from ..models import Export
from ..serializers import ExportSerializer
from core.utils.pagination_utils import CustomPagination
from core.utils.decorators import access_control_middleware
from core.utils.response_utils import success_response, error_response
from django.utils.dateparse import parse_date
from core.utils.helpers import check_if_user_is_staff
from access_control.utils.permission_helpers import *
from access_control.utils.permission_constants import *
from datetime import datetime, time
import logging
from core.utils.date_time_converter import DateTimeConverter
from rest_framework.decorators import api_view
from ..helpers.export_filters import (
    export_search_filter,
    filter_export_by_status,
    filter_export_by_type,
    filter_export_by_app_slug,
    filter_export_by_created_by,
    filter_export_by_date_range,
    filter_by_sort_order,
)   
logger = logging.getLogger(__name__)

def __get_export_queryset(data, business_id):
    filters = {"business_id": business_id}
    is_staff = check_if_user_is_staff(data)

    if is_staff in ["true", True]:
        user_id = data.get("auth_id")
        role_id = data.get("auth_role_id")
        have_view_all_permission = view_modify_all(user_id, role_id, REPORT_EXPORT_VIEW_ALL)
        queryset = Export.objects.filter(**filters)
        if not have_view_all_permission:
            queryset = queryset.filter(created_by=user_id)
        return queryset

    return Export.objects.filter(**filters)


def __apply_export_filters(queryset, filters):
    queryset = export_search_filter(queryset, filters)
    queryset = filter_export_by_status(queryset, filters)
    queryset = filter_export_by_type(queryset, filters)
    queryset = filter_export_by_app_slug(queryset, filters)
    queryset = filter_export_by_created_by(queryset, filters)
    queryset = filter_export_by_date_range(queryset, filters)
    queryset = filter_by_sort_order(queryset, filters)
    return queryset


@api_view(["POST"])
@access_control_middleware
def report_export_list(request):
    data = request.data
    business_id = data.get("auth_business_id")
    timezone = data.get("auth_timezone")

    last_segment = request.path.rstrip("/").split("/")[-1]

    # normalize list values from request.data (QueryDict behaviour)
    filter_data = {
        k: v[0] if isinstance(v, list) and len(v) == 1 else v
        for k, v in data.items()
    }
    filter_data["app_slug"] = last_segment

    queryset = __get_export_queryset(data, business_id)
    queryset = __apply_export_filters(queryset, filter_data).order_by("-created_at")

    paginator = CustomPagination()
    page = paginator.paginate_queryset(queryset, request)

    result = ExportSerializer(page, many=True).data
    for d in result:
        d["created_at"] = DateTimeConverter.from_utc_datetime(d["created_at"], timezone)
        d["createdAt"] = d["created_at"]

    return success_response(
        "records_fetched",
        status.HTTP_200_OK,
        paginator.get_paginated_response(result),
    )


@api_view(['POST'])
@access_control_middleware
def report_export_update(request, pk):
    business_id = request.data.get("auth_business_id")

    if not pk:
        return error_response("missing_id", status.HTTP_400_BAD_REQUEST)

    obj = Export.objects.filter(pk=pk, business_id=business_id).first()
    if not obj:
        return error_response("record_not_found", status.HTTP_404_NOT_FOUND)

    data = {
        "status": request.data.get("status"),
        "link": request.data.get("link"),
    }

    serializer = ExportSerializer(obj, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return success_response("record_updated", status.HTTP_200_OK, serializer.data)

    return error_response("record_update_failed", status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)