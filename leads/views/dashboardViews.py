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
    filter_by_priority, 
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
    queryset = filter_by_priority(queryset, filters)
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
        queryset
        .values('stage__id', 'stage__name', 'stage__type')
        .annotate(count=Count('id'))
    )

    stages_summary = []

    for stage in stage_counts:
        percentage = (stage['count'] / total_leads) * 100 if total_leads > 0 else 0

        stages_summary.append({
            "name": stage['stage__name'],
            "type": stage['stage__type'],
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
            if branch_id:
                queryset = queryset.filter(branch_id=branch_id)

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
            is_active=True
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

    # Only lost leads
    lost_leads = queryset.filter(stage_id__in=lost_stage_ids)
    total_lost_leads = lost_leads.count()

    # 🔥 Subquery to get latest StageReasonEntry per lead
    latest_entry_subquery = StageReasonEntry.objects.filter(
        lead=OuterRef('lead_id'),
        stage_id__in=lost_stage_ids
    ).order_by('-created_at')  # latest first

    latest_entries = StageReasonEntry.objects.filter(
        id__in=Subquery(latest_entry_subquery.values('id')[:1])
    )

    # Aggregate by reason
    lost_reason_summary = latest_entries.values(
        reason=F("stage_reason__name")
    ).annotate(
        count=Count("lead", distinct=True)
    )

    reasons_with_percentage = [
        {
            "reason": entry["reason"] or "Unknown",
            "count": entry["count"],
            "percentage": round((entry["count"] / total_lost_leads) * 100, 2)
            if total_lost_leads > 0 else 0
        }
        for entry in lost_reason_summary
    ]

    data = {
        "total_leads": total_lost_leads,
        "lost_reasons": reasons_with_percentage
    }

    return success_response("record_fetched", status.HTTP_200_OK, data)

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
    ).order_by("-day")  # latest day first

    # Format as desired dictionary
    trend_data = {
        entry["day"].strftime("%b %d"): {
            "leads_created": entry["lead_created"],
            "students_won": entry["leads_won"]
        }
        for entry in trend_qs
    }

    return success_response("record_fetched", status.HTTP_200_OK, {"trend": trend_data})

# def get_stages_leads(request):
#     business_id = request.query_params.get('auth_business_id')
#     queryset = get_queryset(request, business_id)
#     queryset = apply_filters(queryset, request.query_params)
#     leads_count = queryset.count()

    
#     active_stages = list(Stage.objects.filter(is_active=True, business_id=business_id, type=type).order_by('priority').values("name", "status"))
#     lead_stages = queryset.values(stage_name=F('stage__name')).annotate(count=Count('id'))
#     lead_stages_dict = {entry["stage_name"]: entry["count"] for entry in lead_stages}
#     stages_with_counts = [
#         {
#             "stage_name": stage["name"],
#             "count": lead_stages_dict.get(stage["name"], 0)  # Default to 0 if not found
#         }
#         for stage in active_stages
#     ]
#     data = {"total": leads_count, "stages": stages_with_counts}
#     return data

# def get_funnel_stages(request):
#     business_id = request.query_params.get('auth_business_id')

#     lost_stage = Stage.objects.filter(
#         business_id=business_id,
#         status="lost"
#     ).first()

#     queryset = get_queryset(request, business_id)
#     queryset = apply_filters(queryset, request.query_params)

#     # Exclude lost + NULL stages
#     if lost_stage:
#         queryset = queryset.exclude(Q(stage=lost_stage) | Q(stage__isnull=True))

#     # Active (non-lost) stages
#     active_stages = list(
#         Stage.objects.filter(
#             is_active=True,
#             business_id=business_id,
#         )
#         .exclude(status="lost")
#         .order_by("priority")
#         .values("name", "status")
#     )

#     # Stage-wise lead counts
#     lead_stages = queryset.values(
#         stage_name=F("stage__name")
#     ).annotate(count=Count("id"))

#     lead_stages_dict = {
#         entry["stage_name"]: entry["count"]
#         for entry in lead_stages
#         if entry["stage_name"]
#     }

#     # ✅ Total leads only from active stages
#     active_stage_names = {s["name"] for s in active_stages}
#     leads_count = sum(
#         entry["count"]
#         for entry in lead_stages
#         if entry["stage_name"] in active_stage_names
#     )

#     # Funnel cumulative logic
#     cumulative_count = leads_count
#     stages_with_counts = []

#     for stage_entry in active_stages:
#         stage_name = stage_entry["name"]
#         stage_count = lead_stages_dict.get(stage_name, 0)

#         stages_with_counts.append({
#             "stage_name": stage_name,
#             "count": cumulative_count
#         })

#         cumulative_count -= stage_count

#     return {
#         "total": leads_count,
#         "stages": stages_with_counts
#     }

# def get_tags_leads(request):
#     business_id = request.query_params.get('auth_business_id')
#     queryset = get_queryset(request, business_id)
#     queryset = apply_filters(queryset, request.query_params)
#     leads_count = queryset.count()
#     active_tags = list(Tag.objects.filter(is_active=True, business_id=business_id).values_list("name", flat=True))
#     lead_tags = queryset.values(tag_name=F('tag__name')).annotate(count=Count('id'))
#     lead_tags_dict = {entry["tag_name"]: entry["count"] for entry in lead_tags}
#     tags_with_counts = [
#         {
#             "tag_name": tag,
#             "count": lead_tags_dict.get(tag, 0)  # Default to 0 if not found
#         }
#         for tag in active_tags
#     ]
#     data = {"total": leads_count, "tags": tags_with_counts}
#     return data

# def get_branches_leads(request):
#     business_id = request.query_params.get('auth_business_id')
#     queryset = get_queryset(request, business_id)
#     queryset = apply_filters(queryset, request.query_params)
#     leads_count = queryset.count()
#     lead_branches = (queryset.values("branch_id").annotate(count=Count('id')))
#     data = {"total": leads_count,"branches": list(lead_branches)}
#     return data

# def get_sessions_leads(request):
#     business_id = request.query_params.get('auth_business_id')
#     queryset = get_queryset(request, business_id)
#     queryset = apply_filters(queryset, request.query_params)
#     leads_count = queryset.count()
#     lead_sessions = (queryset.values("session_id").annotate(count=Count('id')))
#     data = {"total": leads_count,"sessions": list(lead_sessions)}
#     return data

# def get_monthly_leads(request):
#     business_id = request.query_params.get('auth_business_id')
#     data = {"last_12_months": [], "last_6_months": [], "last_30_days": [], "last_7_days": []}
#     queryset = get_queryset(request, business_id)
#     queryset = apply_filters(queryset, request.query_params)
#     days_and_months = get_last_months_and_days()
#     data, queryset = calculate_last_months(queryset, days_and_months, data)
#     data = calculate_last_days(queryset, days_and_months, data)
#     return data

# @api_view(['GET'])
# def leads_by_source(request):
#     data = get_sources_leads(request)
#     return success_response("record_fetched", status.HTTP_200_OK, data)

# @api_view(['GET'])
# def leads_by_medium(request):
#     data = get_mediums_leads(request)
#     return success_response("record_fetched", status.HTTP_200_OK, data)

# @api_view(['GET'])
# def leads_by_stage(request):
#     data = get_stages_leads(request)
#     return success_response("record_fetched", status.HTTP_200_OK, data)

# @api_view(['GET'])
# def funnel_stages(request):
#     data = get_funnel_stages(request)
#     return success_response("record_fetched", status.HTTP_200_OK, data)

# @api_view(['GET'])
# def leads_by_tag(request):
#     data = get_tags_leads(request)
#     return success_response("record_fetched", status.HTTP_200_OK, data)

# @api_view(['GET'])
# def leads_by_branch(request):
#     data = get_branches_leads(request)
#     return success_response("record_fetched", status.HTTP_200_OK, data)

# @api_view(['GET'])
# def leads_by_session(request):
#     data = get_sessions_leads(request)
#     return success_response("record_fetched", status.HTTP_200_OK, data)

# @api_view(['GET'])
# def monthly_leads(request):
#     data = get_monthly_leads(request)
#     return success_response("record_fetched", status.HTTP_200_OK, data)


# def calculate_last_months(queryset, days_and_months, data):
#     # Get all month-year combinations for last 12 months (+1 previous month)
#     all_months = days_and_months["last_12_months"][:]  # Copy to avoid modifying original
#     previous_month = get_previous_month_year(all_months[0])
#     all_months.insert(0, previous_month)  # Add previous month at the start

#     # Convert to (year, month) tuples
#     month_year_pairs = [(int(y), month_to_digit(m)) for m, y in (entry.split('-') for entry in all_months)]

#     # Fetch lead counts in one query
#     lead_counts = (
#         queryset.filter(created_at__year__in=[y for y, _ in month_year_pairs], created_at__month__in=[m for _, m in month_year_pairs])
#         .values("created_at__year", "created_at__month")
#         .annotate(count=Count("id"))
#     )

#     # Convert query result to dictionary {(year, month): count}
#     lead_counts_dict = {(entry["created_at__year"], entry["created_at__month"]): entry["count"] for entry in lead_counts}

#     total_leads_last_12 = 0  # Total count for last 12 months
#     total_leads_last_6 = 0  # Total count for last 6 months

#     # Process results in a single loop
#     for i in range(1, len(all_months)):  # Start from index 1 to skip previous_month
#         current_month, current_year = all_months[i].split('-')
#         current_year = int(current_year)
#         current_month_digit = month_to_digit(current_month)

#         previous_month, previous_year = all_months[i - 1].split('-')
#         previous_year = int(previous_year)
#         previous_month_digit = month_to_digit(previous_month)

#         this_month_count = lead_counts_dict.get((current_year, current_month_digit), 0)
#         last_month_count = lead_counts_dict.get((previous_year, previous_month_digit), 0)

#         data["last_12_months"].append({
#             "month": current_month,
#             "thisMonth": this_month_count,
#             "lastMonth": last_month_count
#         })

#         total_leads_last_12 += this_month_count  # Update total count for last 12 months

#     # Extract last 6 months from last_12_months list
#     data["last_6_months"] = data["last_12_months"][-6:]

#     # Calculate total leads for the last 6 months
#     total_leads_last_6 = sum(entry["thisMonth"] for entry in data["last_6_months"])

#     # Add total leads count to the data dictionary
#     data["total_leads_last_12_months"] = total_leads_last_12
#     data["total_leads_last_6_months"] = total_leads_last_6

#     return data, queryset


# def calculate_last_days(queryset, days_and_months, data):
#     # Get the list of dates
#     date_list = days_and_months["last_30_days"][:]  # Copy to avoid modifying the original
#     previous_date = get_previous_date(date_list[0])  # Get the previous date
#     date_list.insert(0, previous_date)  # Add the previous date at the start

#     # Count leads per date in a single query
#     lead_counts = (
#         queryset.filter(created_at__date__in=date_list)
#         .values("created_at__date")
#         .annotate(count=Count("id"))
#     )

#     # Convert result to dictionary format { "YYYY-MM-DD": count }
#     lead_counts_dict = {str(entry["created_at__date"]): entry["count"] for entry in lead_counts}

#     total_leads_last_30 = 0  # Total count for last 30 days
#     total_leads_last_7 = 0  # Total count for last 7 days

#     # Process results
#     for i, date in enumerate(date_list):
#         if date == previous_date:  # **Skip the previous_date**
#             continue

#         this_day_count = lead_counts_dict.get(date, 0)
#         last_day_count = lead_counts_dict.get(date_list[i - 1], 0) if i > 0 else 0  # Get previous day's count

#         data["last_30_days"].append({
#             "day": date,
#             "thisDay": this_day_count,
#             "lastDay": last_day_count
#         })

#         total_leads_last_30 += this_day_count  # Update total count for last 30 days

#     # Extract last 7 days from last_30_days list
#     data["last_7_days"] = data["last_30_days"][-7:]

#     # Calculate total leads for the last 7 days
#     total_leads_last_7 = sum(entry["thisDay"] for entry in data["last_7_days"])

#     # Add total leads count to the data dictionary
#     data["total_leads_last_30_days"] = total_leads_last_30
#     data["total_leads_last_7_days"] = total_leads_last_7

#     return data
