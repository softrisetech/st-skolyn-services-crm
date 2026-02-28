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

logger = logging.getLogger(__name__)


class ReportExportListAPIView(APIView):
    pagination_class = CustomPagination

    def get_queryset(self, request, auth_business_id):
        filters = {"business_id": auth_business_id}
        data = request.data
        is_staff = check_if_user_is_staff(data)

        if is_staff == "true":
            user_id = data.get('auth_id')
            role_id = data.get('auth_role_id')
            have_view_all_permission = view_modify_all(user_id, role_id, REPORT_EXPORT_VIEW_ALL)
            queryset = Export.objects.filter(**filters)
            if not have_view_all_permission:
                queryset = queryset.filter(created_by=user_id)
            return queryset

        return Export.objects.filter(**filters)

    def apply_filters(self, queryset, filters):
        normalized_filters = {}
        for key, value in filters.items():
            normalized_filters[key] = value[0] if isinstance(value, list) and len(value) == 1 else value
        filters = normalized_filters

        search = filters.get("search")
        if search:
            queryset = queryset.filter(
                Q(app_slug__icontains=search)
                | Q(type__icontains=search)
                | Q(status__icontains=search)
            )

        status_filter = filters.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        export_type = filters.get("type")
        if export_type:
            queryset = queryset.filter(type=export_type)

        app_slug = filters.get("app_slug")
        if app_slug:
            queryset = queryset.filter(app_slug=app_slug)

        created_by = filters.get("created_by")
        if created_by:
            if isinstance(created_by, list):
                queryset = queryset.filter(created_by__in=created_by)
            else:
                queryset = queryset.filter(created_by__in=str(created_by).split(","))

        from_date = filters.get("from_date")
        to_date = filters.get("to_date")

        if from_date:
            queryset = queryset.filter(updated_at__gte=datetime.combine(parse_date(from_date), time.min))
        if to_date:
            queryset = queryset.filter(updated_at__lte=datetime.combine(parse_date(to_date), time.max))

        return queryset

    @access_control_middleware
    def post(self, request):
        business_id = request.data.get("auth_business_id")
        timezone = request.data.get("auth_timezone")

        last_segment = request.path.rstrip("/").split("/")[-1]
        queryset = self.get_queryset(request, business_id)

        filters = dict(request.data)
        filters["app_slug"] = last_segment

        queryset = self.apply_filters(queryset, filters).order_by("-created_at")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        data = ExportSerializer(page, many=True).data
        for d in data:
            d["created_at"] = DateTimeConverter.from_utc_datetime(d["created_at"], timezone)
            d["createdAt"] = d["created_at"]

        return success_response(
            "records_fetched",
            status.HTTP_200_OK,
            paginator.get_paginated_response(data),
        )


class ReportExportUpdateAPIView(APIView):
    @access_control_middleware
    def post(self, request, pk):
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