from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from core.utils.decorators import access_control_middleware
from core.utils.pagination_utils import CustomPagination
from core.utils.response_utils import success_response
from core.utils.date_time_converter import DateTimeConverter
from leads.models import Lead, FollowUp
from leads.serializers import LeadListSerializer
from django.db.models import Subquery, OuterRef, Q
from ..views.leadViews import __queryset
from leads.utils.filters import (
    filter_by_sort_order,filter_by_campaigns,filter_by_teams,filter_by_priorities,filter_by_countries,
    filter_by_states,filter_by_cities,lead_search_filter,filter_by_date_range,filter_by_branches,filter_by_created_by,
    filter_by_assigned_to,filter_by_mediums,filter_by_sessions,filter_by_sources,filter_by_stages,filter_by_tags,
)
from report_export.utils.constants import constants
from report_export.utils.export_helpers import export_entry, export_obj

from ..views.followUpViews import __queryset as __followup_queryset

def __apply_filters(queryset, filters):
    queryset = lead_search_filter(queryset, filters)
    queryset = filter_by_branches(queryset, filters)
    queryset = filter_by_sessions(queryset, filters)
    queryset = filter_by_created_by(queryset, filters)
    queryset = filter_by_assigned_to(queryset, filters)
    queryset = filter_by_countries(queryset, filters)
    queryset = filter_by_states(queryset, filters)
    queryset = filter_by_cities(queryset, filters)
    queryset = filter_by_priorities(queryset, filters)
    queryset = filter_by_mediums(queryset, filters)
    queryset = filter_by_sources(queryset, filters)
    queryset = filter_by_stages(queryset, filters)
    queryset = filter_by_tags(queryset, filters)
    queryset = filter_by_teams(queryset, filters)
    queryset = filter_by_campaigns(queryset, filters)
    queryset = filter_by_date_range(queryset, filters)
    queryset = filter_by_sort_order(queryset, filters)
    return queryset



@api_view(['POST'])
@access_control_middleware
def get_high_priority_no_followup_leads(request):
    data = request.data
    business_id = data.get('auth_business_id')
    userTimezone = data.get("auth_timezone")

    threshold = timezone.now() - timezone.timedelta(hours=48)

    recent_followups = __followup_queryset(business_id, OuterRef('pk'), use_report_db=True).filter(
        date_time__gte=threshold
    )
    queryset = __queryset(data, business_id, use_report_db=True).filter(
        priority=1,
    ).exclude(
        stage__type__in=['won', 'lost']
    ).filter(
        ~Q(id__in=Subquery(recent_followups.values('lead_id')))
    ).select_related(
        'stage', 'medium', 'source', 'tag', 'team', 'campaign', 'contact',
    )
    queryset = __apply_filters(queryset, data)
        
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = LeadListSerializer(paginated_queryset, many=True).data

    for item in serialized_data:
        if item.get("imported_at"):
            item["imported_at"] = DateTimeConverter.from_utc_datetime(item["imported_at"], userTimezone)
        item["created_at"] = DateTimeConverter.from_utc_datetime(item["created_at"], userTimezone)
        item["updated_at"] = DateTimeConverter.from_utc_datetime(item["updated_at"], userTimezone)

    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)

@api_view(['POST'])
@access_control_middleware
def get_no_followup_leads(request):

    data = request.data
    business_id = data.get('auth_business_id')
    userTimezone = data.get("auth_timezone")

    has_followup =__followup_queryset(business_id, OuterRef('pk'), use_report_db=True)

    queryset = __queryset(data, business_id, use_report_db=True).exclude(
        stage__type__in=['won', 'lost']
    ).filter(
        ~Q(id__in=Subquery(has_followup.values('lead_id')))
    ).select_related(
        'stage', 'medium', 'source', 'tag', 'team', 'campaign', 'contact',
    )

    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = LeadListSerializer(paginated_queryset, many=True).data

    for item in serialized_data:
        if item.get("imported_at"):
            item["imported_at"] = DateTimeConverter.from_utc_datetime(item["imported_at"], userTimezone)
        item["created_at"] = DateTimeConverter.from_utc_datetime(item["created_at"], userTimezone)
        item["updated_at"] = DateTimeConverter.from_utc_datetime(item["updated_at"], userTimezone)

    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)

@api_view(['POST'])
@access_control_middleware
def get_upcoming_followup_leads(request):
    data = request.data
    business_id = data.get('auth_business_id')
    userTimezone = data.get("auth_timezone")
    now = timezone.now()
    upcoming_followups =__followup_queryset(business_id, OuterRef('pk'), use_report_db=True).filter(
        date_time__gte=now,
        is_done=False,
    )

    queryset = __queryset(data, business_id, use_report_db=True).exclude(
        stage__type__in=['won', 'lost']
    ).filter(
        Q(id__in=Subquery(upcoming_followups.values('lead_id')))
    ).select_related(
        'stage', 'medium', 'source', 'tag', 'team', 'campaign', 'contact',
    )

    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = LeadListSerializer(paginated_queryset, many=True).data

    for item in serialized_data:
        if item.get("imported_at"):
            item["imported_at"] = DateTimeConverter.from_utc_datetime(item["imported_at"], userTimezone)
        item["created_at"] = DateTimeConverter.from_utc_datetime(item["created_at"], userTimezone)
        item["updated_at"] = DateTimeConverter.from_utc_datetime(item["updated_at"], userTimezone)

    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)

@api_view(['POST'])
@access_control_middleware
def get_overdue_followup_leads(request):

    data = request.data
    business_id = data.get('auth_business_id')
    userTimezone = data.get("auth_timezone")
    
    now = timezone.now()

    overdue_followups =__followup_queryset(business_id, OuterRef('pk'), use_report_db=True).filter(
        date_time__lt=now,
        is_done=False,
    )

    queryset = __queryset(data, business_id, use_report_db=True).exclude(
        stage__type__in=['won', 'lost']
    ).filter(
        Q(id__in=Subquery(overdue_followups.values('lead_id')))
    ).select_related(
        'stage', 'medium', 'source', 'tag', 'team', 'campaign', 'contact',
    )

    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = LeadListSerializer(paginated_queryset, many=True).data

    for item in serialized_data:
        if item.get("imported_at"):
            item["imported_at"] = DateTimeConverter.from_utc_datetime(item["imported_at"], userTimezone)
        item["created_at"] = DateTimeConverter.from_utc_datetime(item["created_at"], userTimezone)
        item["updated_at"] = DateTimeConverter.from_utc_datetime(item["updated_at"], userTimezone)

    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)


@api_view(['POST'])
@access_control_middleware
def get_lost_leads(request):
    data = request.data
    business_id = data.get('auth_business_id')
    userTimezone = data.get("auth_timezone")

    queryset = __queryset(data, business_id, use_report_db=True).filter(
        stage__type='lost',
    ).select_related(
        'stage', 'medium', 'source', 'tag', 'team', 'campaign', 'contact',
    ).prefetch_related(
        'stagereasonentry_set__stage_reason'
    )

    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = LeadListSerializer(paginated_queryset, many=True).data

    reason_map = {
        str(lead.id): lead.stagereasonentry_set.first()
        for lead in paginated_queryset
    }    
    
    for item in serialized_data:
        if item.get("imported_at"):
            item["imported_at"] = DateTimeConverter.from_utc_datetime(item["imported_at"], userTimezone)
        item["created_at"] = DateTimeConverter.from_utc_datetime(item["created_at"], userTimezone)
        item["updated_at"] = DateTimeConverter.from_utc_datetime(item["updated_at"], userTimezone)

        entry = reason_map.get(item["id"])
        item["lost_reason"] = {
            "id": str(entry.stage_reason.id),
            "reason": entry.stage_reason.name,
            "remarks": entry.remarks,
        } if entry else None

    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)