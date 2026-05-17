import calendar
from django.db.models import Q
from rest_framework import status
from collections import defaultdict
from django.db.models import Count, F, OuterRef, Subquery
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from access_control.utils.permission_helpers import *
from core.utils.response_utils import success_response
from access_control.utils.permission_constants import *
from ..models import Lead, Source, Medium, Stage, Campaign, StageReasonEntry, SessionTarget
from ..serializers import DashboardCampaignSerializer
from core.utils.pagination_utils import CustomPagination
from core.constants.model_constants import WON, LOST
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncDate
from django.db.models import Sum

from leads.utils.filters import (
    filter_by_classes, 
    filter_by_sort_order, 
    filter_by_campaigns, 
    filter_by_teams, 
    filter_by_priorities, 
    filter_by_countries, 
    filter_by_states, 
    filter_by_cities, 
    lead_search_filter, 
    filter_by_date_range, 
    filter_by_branches, 
    filter_by_created_by, 
    filter_by_assigned_to, 
    filter_by_mediums, 
    filter_by_sessions, 
    filter_by_sources, 
    filter_by_stages, 
    filter_by_tags,
    filter_by_active
)
from core.utils.helpers import (
    get_last_months_and_days, 
    month_to_digit, 
    get_previous_month_year, 
    get_previous_date, 
    check_if_user_is_staff
)

def __queryset(data, business_id):
    filters = {"business_id": business_id}
    is_staff = check_if_user_is_staff(data)
    if is_staff in ["true", True]:
        user_id = data.get('auth_id')
        role_id = data.get('auth_role_id')
        view_all = LEAD_VIEW_ALL
        branch_wise = LEAD_BRANCH_WISE
        have_read_permission = view_modify_all(user_id, role_id, LEAD_READ)
        have_view_all_permission = view_modify_all(user_id, role_id, view_all)
        have_branch_wise_permission = view_branch_wise(user_id, role_id, branch_wise)

        if not have_read_permission:
            return Lead.objects.none()
        
        queryset = Lead.objects.filter(**filters)

        if not have_view_all_permission:
            # Add OR condition: created_by=user_id OR assigned_to=user_id
            queryset = queryset.filter(Q(created_by=user_id) | Q(assigned_to=user_id))

        if have_branch_wise_permission:
            branch_id = data.get("auth_branch_id")
            queryset = queryset.filter(branch_id=branch_id)

        return queryset

    return Lead.objects.filter(**filters)


def __apply_filters(queryset, filters):
    queryset = lead_search_filter(queryset, filters)
    queryset = filter_by_branches(queryset, filters)
    queryset = filter_by_sessions(queryset, filters)
    queryset = filter_by_classes(queryset, filters)
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
def get_leads_summary(request):
    data = request.data
    business_id = data.get('auth_business_id')

    queryset = __queryset(data, business_id)
    queryset = __apply_filters(queryset, data)

    total_leads = queryset.count()

    # Dynamic stage-wise counts
    stage_counts = (
        Stage.objects
        .filter(business_id=business_id)
        .annotate(
            count=Count(
                'lead',
                filter=Q(lead__in=queryset)
            )
        )
        .values(
            'id',
            'name',
            'type',
            'priority',
            'count'
        )
        .order_by('priority')
    )

    stages_summary = []

    for stage in stage_counts:
        percentage = (stage['count'] / total_leads) * 100 if total_leads > 0 else 0

        stages_summary.append({
            "name": stage['name'],
            "type": stage['type'],
            "count": stage['count'],
            "percentage": round(percentage, 2)
        })

    # Optional system KPIs
    won_leads = sum(s['count'] for s in stages_summary if s['type'] == WON)
    conversion_rate = round((won_leads / total_leads) * 100, 2) if total_leads > 0 else 0

    summary = {
        "total_leads": total_leads,
        "conversion_rate": conversion_rate,
        "stages": stages_summary
    }

    return success_response("record_fetched", status.HTTP_200_OK, summary)


def get_session_target(data, business_id):
    filters = {"business_id": business_id}

    is_staff = check_if_user_is_staff(data)
    queryset = SessionTarget.objects.filter(**filters)

    # 🔹 Staff-specific branch restriction
    if is_staff in ["true", True]:
        user_id = data.get('auth_id')
        role_id = data.get('auth_role_id')

        have_branch_wise_permission = view_branch_wise(
            user_id,
            role_id,
            SESSION_TARGET_BRANCH_WISE
        )

        # If user does NOT have permission → restrict to own branch
        if not have_branch_wise_permission:
            branch_id = data.get("auth_branch_id")

            additional_branch_ids = data.get("auth_additional_branch_ids", [])
            all_branch_ids = list(filter(None, [branch_id] + (additional_branch_ids if isinstance(additional_branch_ids, list) else [])))

            if all_branch_ids:
                queryset = queryset.filter(branch_id__in=all_branch_ids)

    queryset = filter_by_branches(queryset, data)
    queryset = filter_by_sessions(queryset, data)

    # 🔹 Always return SUM
    total_target = queryset.aggregate(total=Sum("target"))["total"] or 0

    return total_target

@api_view(['POST'])
def get_leads_funnel(request):
    data = request.data
    business_id = data.get("auth_business_id")

    queryset = __queryset(data, business_id)
    queryset = __apply_filters(queryset, data)

    total_leads = queryset.count()

    # 🔹 total target
    total_target = get_session_target(data, business_id)

    return success_response("record_fetched", status.HTTP_200_OK, {
        "total_leads": total_leads,
        "total_target": total_target,
        "funnel": []
    })

    # 🔹 remove lost/null
    lost_stage_ids = Stage.objects.filter(
        business_id=business_id,
        type=LOST
    ).values_list("id", flat=True)

    queryset = queryset.exclude(
        Q(stage__id__in=lost_stage_ids) | Q(stage__isnull=True)
    )

    # 🔹 ordered stages
    stages = list(
        Stage.objects.filter(
            business_id=business_id,
            # is_active=True
        )
        .exclude(type=LOST)
        .order_by("priority")
        .values("id", "name", "priority")
    )

    # 🔥 KEY: Build dynamic aggregation
    aggregation = {}

    for stage in stages:
        key = f"stage_{stage['id']}"
        aggregation[key] = Count(
            "id",
            filter=Q(stage__priority__gte=stage["priority"])
        )

    # 🔹 single DB hit
    counts = queryset.aggregate(**aggregation)

    # 🔹 build response
    funnel = []

    # ✅ 1. Add TOTAL LEADS at top
    total_leads_conversion = (
        (total_leads / total_target) * 100
        if total_target > 0 else 0
    )

    funnel.append({
        "stage_name": "Total Leads",
        "stage_count": total_leads,
        "funnel_conversion_percentage": 100.0 if total_leads > 0 else 0,
        "target_conversion_percentage": round(total_leads_conversion, 2)
    })

    # ✅ 2. Add stage-wise waterfall
    for stage in stages:
        key = f"stage_{stage['id']}"
        stage_count = counts.get(key, 0)
        stage_name = stage["name"]

        funnel_conversion = (
            (stage_count / total_leads) * 100
            if total_leads > 0 else 0
        )

        target_conversion = (
            (stage_count / total_target) * 100
            if total_target > 0 else 0
        )

        funnel.append({
            "stage_name": stage_name,
            "stage_count": stage_count,
            "funnel_conversion_percentage": round(funnel_conversion, 2),
            "target_conversion_percentage": round(target_conversion, 2)
        })

    return success_response("record_fetched", status.HTTP_200_OK, {
        "total_leads": total_leads,
        "total_target": total_target,
        "funnel": funnel
    })

@api_view(['POST'])
def get_sources_leads(request):
    data = request.data
    business_id = data.get('auth_business_id')
    queryset = __queryset(data, business_id)
    queryset = __apply_filters(queryset, data)
    leads_count = queryset.count()
    all_sources = list(Source.objects.filter(is_active=True, business_id=business_id).values_list("name", flat=True))
    lead_sources = (
        queryset.values(source_name=F('source__name'))
        .annotate(count=Count('id'))
    )
    lead_sources_dict = {entry["source_name"]: entry["count"] for entry in lead_sources}
    sources_with_percentage = [
        {
            "name": source,
            "count": lead_sources_dict.get(source, 0),  # Default to 0 if not found
            "percentage": round((lead_sources_dict.get(source, 0) / leads_count) * 100, 2) if leads_count > 0 else 0
        }
        for source in all_sources
    ]
    data = {"total_leads": leads_count, "sources": sources_with_percentage}
    return success_response("record_fetched", status.HTTP_200_OK, data)

@api_view(['POST'])
def get_mediums_leads(request):
    data = request.data
    business_id = data.get('auth_business_id')
    queryset = __queryset(data, business_id)
    queryset = __apply_filters(queryset, data)
    leads_count = queryset.count()
    active_mediums = list(Medium.objects.filter(is_active=True, business_id=business_id).values_list("name", flat=True))
    lead_mediums = (queryset.values(medium_name=F('medium__name')).annotate(count=Count('id')))
    lead_mediums_dict = {entry["medium_name"]: entry["count"] for entry in lead_mediums}
    mediums_with_percentage = [
        {
            "name": medium,
            "count": lead_mediums_dict.get(medium, 0),  # Default to 0 if not found
            "percentage": round((lead_mediums_dict.get(medium, 0) / leads_count) * 100, 2) if leads_count > 0 else 0
        }
        for medium in active_mediums
    ]

    data = {"total_leads": leads_count, "mediums": mediums_with_percentage}
    return success_response("record_fetched", status.HTTP_200_OK, data)

@api_view(['POST'])
def get_campaigns_leads(request):
    data = request.data
    business_id = data.get('auth_business_id')

    campaigns_qs = Campaign.objects.filter(
        is_active=True,
        business_id=business_id
    )

    campaigns_qs = filter_by_active(campaigns_qs, data)
    campaigns_qs = filter_by_sort_order(campaigns_qs, data)

    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(campaigns_qs, request)

    campaign_ids = [str(c.id) for c in paginated_queryset]

    # Get WON stages
    won_stage_ids = Stage.objects.filter(
        business_id=business_id,
        type=WON
    ).values_list("id", flat=True)

    # Base lead queryset
    leads_qs = __queryset(data, business_id).filter(campaign_id__in=campaign_ids)
    leads_qs = __apply_filters(leads_qs, data)

    # 🔥 Aggregate leads in ONE query
    leads_summary = leads_qs.values("campaign_id").annotate(
        total_leads=Count("id"),
        won_leads=Count("id", filter=Q(stage_id__in=won_stage_ids))
    )

    leads_summary_map = {
        str(item["campaign_id"]): item
        for item in leads_summary
    }

    serialized_data = DashboardCampaignSerializer(paginated_queryset, many=True).data

    for campaign in serialized_data:
        summary = leads_summary_map.get(campaign['id'], {})
        total = summary.get("total_leads", 0)
        won = summary.get("won_leads", 0)

        campaign['total_leads'] = total
        campaign['won_leads'] = won
        campaign['conversion_rate'] = round((won / total) * 100, 2) if total > 0 else 0

    response_data = paginator.get_paginated_response(serialized_data)

    return success_response('record_fetched', status.HTTP_200_OK, response_data)

@api_view(['POST'])
def get_assigned_leads(request):
    data = request.data
    business_id = data.get('auth_business_id')

    queryset = __queryset(data, business_id)
    queryset = __apply_filters(queryset, data)

    total_leads = queryset.count()

    queryset = queryset.filter(assigned_to__isnull=False)

    # WON stages
    won_stage_ids = Stage.objects.filter(
        business_id=business_id,
        type=WON
    ).values_list("id", flat=True)

    # 🔥 Aggregate by assigned_to UUID
    assigned_summary = queryset.values("assigned_to").annotate(
        total_assigned=Count("id"),
        won_assigned=Count("id", filter=Q(stage_id__in=won_stage_ids))
    )

    assigned_with_percentage = []

    for entry in assigned_summary:
        assigned_id = entry["assigned_to"]
        total = entry["total_assigned"]
        won = entry["won_assigned"]

        assigned_with_percentage.append({
            "assigned_to": assigned_id,
            "leads_handled": total,
            "students_won": won
        })

    data = {
        "total_leads": total_leads,
        "assigned_leads": assigned_with_percentage
    }

    return success_response("record_fetched", status.HTTP_200_OK, data)


@api_view(['POST'])
def get_lost_leads_by_reason(request):
    data = request.data
    business_id = data.get('auth_business_id')

    queryset = __queryset(data, business_id)
    queryset = __apply_filters(queryset, data)

    # LOST stages
    lost_stage_ids = Stage.objects.filter(
        business_id=business_id,
        type=LOST
    ).values_list("id", flat=True)

    # Only leads whose CURRENT stage is LOST
    lost_leads = queryset.filter(stage_id__in=lost_stage_ids)

    total_lost_leads = lost_leads.count()

    # Latest lost reason entry per lead
    latest_reason_entry = StageReasonEntry.objects.filter(
        lead_id=OuterRef('pk'),
        stage_id__in=lost_stage_ids
    ).order_by('-created_at')

    # Annotate latest reason entry id
    lost_leads = lost_leads.annotate(
        latest_reason_entry_id=Subquery(
            latest_reason_entry.values('id')[:1]
        )
    )

    # Fetch latest entries
    latest_entries = StageReasonEntry.objects.filter(
        id__in=lost_leads.values('latest_reason_entry_id')
    )

    # Aggregate reason counts
    lost_reason_summary = latest_entries.values(
        reason=F('stage_reason__name')
    ).annotate(
        count=Count('lead_id', distinct=True)
    ).order_by('-count')

    reasons_with_percentage = [
        {
            "reason": item["reason"] or "Unknown",
            "count": item["count"],
            "percentage": round(
                (item["count"] / total_lost_leads) * 100, 2
            ) if total_lost_leads > 0 else 0
        }
        for item in lost_reason_summary
    ]

    response_data = {
        "total_leads": total_lost_leads,
        "lost_reasons": reasons_with_percentage
    }

    return success_response(
        "record_fetched",
        status.HTTP_200_OK,
        response_data
    )

@api_view(['POST'])
def get_leads_conversion_trend(request):
    data = request.data
    business_id = data.get('auth_business_id')
    months = int(data.get('months', 3))  # number of months to include

    queryset = __queryset(data, business_id)
    queryset = __apply_filters(queryset, data)

    # Get WON stages
    won_stage_ids = Stage.objects.filter(
        business_id=business_id,
        type=WON
    ).values_list("id", flat=True)

    # Filter last N months
    start_date = (datetime.now() - relativedelta(months=months)).replace(day=1)
    queryset = queryset.filter(created_at__date__gte=start_date)

    # Truncate by day
    trend_qs = queryset.annotate(day=TruncDate("created_at")).values("day").annotate(
        lead_created=Count("id"),
        leads_won=Count("id", filter=Q(stage_id__in=won_stage_ids))
    ).order_by("day")  # latest day first

    # Format as desired dictionary
    trend_data = {
        entry["day"].strftime("%b %d"): {
            "leads_created": entry["lead_created"],
            "students_won": entry["leads_won"]
        }
        for entry in trend_qs
    }

    return success_response("record_fetched", status.HTTP_200_OK, {"trend": trend_data})
