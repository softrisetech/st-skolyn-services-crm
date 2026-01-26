import calendar
from rest_framework import status
from collections import defaultdict
from django.db.models import Count, F
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from access_control.utils.permission_helpers import *
from core.utils.response_utils import success_response
from access_control.utils.permission_constants import *
from ..models import Lead, Source, Medium, Stage, Tag
from leads.utils.filters import filter_by_branches, filter_by_sessions, filter_by_date_range
from core.utils.helpers import get_last_months_and_days, month_to_digit, get_previous_month_year, get_previous_date, check_if_user_is_staff

def apply_filters(queryset, filters):
    queryset = filter_by_branches(queryset, filters)
    queryset = filter_by_sessions(queryset, filters)
    queryset = filter_by_date_range(queryset, filters)
    return queryset

def get_queryset(request, business_id):
    filters = {"business_id":business_id}
    data = request.query_params or request.data
    is_staff = check_if_user_is_staff(data)
    if is_staff == "true":
        user_id = data.get('auth_id')
        role_id = data.get('auth_role_id')
        view_all = LEAD_VIEW_ALL
        branch_wise = LEAD_BRANCH_WISE
        have_view_all_permission = view_modify_all(user_id, role_id, view_all)
        have_branch_wise_permission = view_branch_wise(user_id, role_id, branch_wise)
        queryset = Lead.objects.filter(**filters)

        if not have_view_all_permission:
            # Add OR condition: created_by=user_id OR assigned_to=user_id
            queryset = queryset.filter(Q(created_by=user_id) | Q(assigned_to=user_id))

        if have_branch_wise_permission:
            branch_id = data.get("auth_branch_id")
            queryset = queryset.filter(branch_id=branch_id)

        return queryset

    return Lead.objects.filter(**filters)

def get_sources_leads(request):
    business_id = request.query_params.get('auth_business_id')
    queryset = get_queryset(request, business_id)
    queryset = apply_filters(queryset, request.query_params)
    leads_count = queryset.count()
    all_sources = list(Source.objects.filter(is_active=True, business_id=business_id).values_list("name", flat=True))
    lead_sources = (
        queryset.values(source_name=F('source__name'))
        .annotate(count=Count('id'))
    )
    lead_sources_dict = {entry["source_name"]: entry["count"] for entry in lead_sources}
    sources_with_percentage = [
        {
            "source_name": source,
            "count": lead_sources_dict.get(source, 0),  # Default to 0 if not found
            "percentage": round((lead_sources_dict.get(source, 0) / leads_count) * 100, 2) if leads_count > 0 else 0
        }
        for source in all_sources
    ]
    data = {"total_leads": leads_count, "sources": sources_with_percentage}
    return data

def get_mediums_leads(request):
    business_id = request.query_params.get('auth_business_id')
    queryset = get_queryset(request, business_id)
    queryset = apply_filters(queryset, request.query_params)
    leads_count = queryset.count()
    active_mediums = list(Medium.objects.filter(is_active=True, business_id=business_id).values_list("name", flat=True))
    lead_mediums = (queryset.values(medium_name=F('medium__name')).annotate(count=Count('id')))
    lead_mediums_dict = {entry["medium_name"]: entry["count"] for entry in lead_mediums}
    mediums_with_percentage = [
        {
            "medium_name": medium,
            "count": lead_mediums_dict.get(medium, 0),  # Default to 0 if not found
            "percentage": round((lead_mediums_dict.get(medium, 0) / leads_count) * 100, 2) if leads_count > 0 else 0
        }
        for medium in active_mediums
    ]

    data = {"total_leads": leads_count, "mediums": mediums_with_percentage}
    return data

def get_stages_leads(request):
    business_id = request.query_params.get('auth_business_id')
    queryset = get_queryset(request, business_id)
    queryset = apply_filters(queryset, request.query_params)
    leads_count = queryset.count()

    
    active_stages = list(Stage.objects.filter(is_active=True, business_id=business_id, type=type).order_by('priority').values("name", "status"))
    lead_stages = queryset.values(stage_name=F('stage__name')).annotate(count=Count('id'))
    lead_stages_dict = {entry["stage_name"]: entry["count"] for entry in lead_stages}
    stages_with_counts = [
        {
            "stage_name": stage["name"],
            "count": lead_stages_dict.get(stage["name"], 0)  # Default to 0 if not found
        }
        for stage in active_stages
    ]
    data = {"total": leads_count, "stages": stages_with_counts}
    return data

def get_funnel_stages(request):
    business_id = request.query_params.get('auth_business_id')

    lost_stage = Stage.objects.filter(
        business_id=business_id,
        status="lost"
    ).first()

    queryset = get_queryset(request, business_id)
    queryset = apply_filters(queryset, request.query_params)

    # Exclude lost + NULL stages
    if lost_stage:
        queryset = queryset.exclude(Q(stage=lost_stage) | Q(stage__isnull=True))

    # Active (non-lost) stages
    active_stages = list(
        Stage.objects.filter(
            is_active=True,
            business_id=business_id,
        )
        .exclude(status="lost")
        .order_by("priority")
        .values("name", "status")
    )

    # Stage-wise lead counts
    lead_stages = queryset.values(
        stage_name=F("stage__name")
    ).annotate(count=Count("id"))

    lead_stages_dict = {
        entry["stage_name"]: entry["count"]
        for entry in lead_stages
        if entry["stage_name"]
    }

    # ✅ Total leads only from active stages
    active_stage_names = {s["name"] for s in active_stages}
    leads_count = sum(
        entry["count"]
        for entry in lead_stages
        if entry["stage_name"] in active_stage_names
    )

    # Funnel cumulative logic
    cumulative_count = leads_count
    stages_with_counts = []

    for stage_entry in active_stages:
        stage_name = stage_entry["name"]
        stage_count = lead_stages_dict.get(stage_name, 0)

        stages_with_counts.append({
            "stage_name": stage_name,
            "count": cumulative_count
        })

        cumulative_count -= stage_count

    return {
        "total": leads_count,
        "stages": stages_with_counts
    }

def get_tags_leads(request):
    business_id = request.query_params.get('auth_business_id')
    queryset = get_queryset(request, business_id)
    queryset = apply_filters(queryset, request.query_params)
    leads_count = queryset.count()
    active_tags = list(Tag.objects.filter(is_active=True, business_id=business_id).values_list("name", flat=True))
    lead_tags = queryset.values(tag_name=F('tag__name')).annotate(count=Count('id'))
    lead_tags_dict = {entry["tag_name"]: entry["count"] for entry in lead_tags}
    tags_with_counts = [
        {
            "tag_name": tag,
            "count": lead_tags_dict.get(tag, 0)  # Default to 0 if not found
        }
        for tag in active_tags
    ]
    data = {"total": leads_count, "tags": tags_with_counts}
    return data

def get_branches_leads(request):
    business_id = request.query_params.get('auth_business_id')
    queryset = get_queryset(request, business_id)
    queryset = apply_filters(queryset, request.query_params)
    leads_count = queryset.count()
    lead_branches = (queryset.values("branch_id").annotate(count=Count('id')))
    data = {"total": leads_count,"branches": list(lead_branches)}
    return data

def get_sessions_leads(request):
    business_id = request.query_params.get('auth_business_id')
    queryset = get_queryset(request, business_id)
    queryset = apply_filters(queryset, request.query_params)
    leads_count = queryset.count()
    lead_sessions = (queryset.values("session_id").annotate(count=Count('id')))
    data = {"total": leads_count,"sessions": list(lead_sessions)}
    return data

def get_monthly_leads(request):
    business_id = request.query_params.get('auth_business_id')
    data = {"last_12_months": [], "last_6_months": [], "last_30_days": [], "last_7_days": []}
    queryset = get_queryset(request, business_id)
    queryset = apply_filters(queryset, request.query_params)
    days_and_months = get_last_months_and_days()
    data, queryset = calculate_last_months(queryset, days_and_months, data)
    data = calculate_last_days(queryset, days_and_months, data)
    return data

@api_view(['GET'])
def leads_by_source(request):
    data = get_sources_leads(request)
    return success_response("record_fetched", status.HTTP_200_OK, data)

@api_view(['GET'])
def leads_by_medium(request):
    data = get_mediums_leads(request)
    return success_response("record_fetched", status.HTTP_200_OK, data)

@api_view(['GET'])
def leads_by_stage(request):
    data = get_stages_leads(request)
    return success_response("record_fetched", status.HTTP_200_OK, data)

@api_view(['GET'])
def funnel_stages(request):
    data = get_funnel_stages(request)
    return success_response("record_fetched", status.HTTP_200_OK, data)

@api_view(['GET'])
def leads_by_tag(request):
    data = get_tags_leads(request)
    return success_response("record_fetched", status.HTTP_200_OK, data)

@api_view(['GET'])
def leads_by_branch(request):
    data = get_branches_leads(request)
    return success_response("record_fetched", status.HTTP_200_OK, data)

@api_view(['GET'])
def leads_by_session(request):
    data = get_sessions_leads(request)
    return success_response("record_fetched", status.HTTP_200_OK, data)

@api_view(['GET'])
def monthly_leads(request):
    data = get_monthly_leads(request)
    return success_response("record_fetched", status.HTTP_200_OK, data)


def calculate_last_months(queryset, days_and_months, data):
    # Get all month-year combinations for last 12 months (+1 previous month)
    all_months = days_and_months["last_12_months"][:]  # Copy to avoid modifying original
    previous_month = get_previous_month_year(all_months[0])
    all_months.insert(0, previous_month)  # Add previous month at the start

    # Convert to (year, month) tuples
    month_year_pairs = [(int(y), month_to_digit(m)) for m, y in (entry.split('-') for entry in all_months)]

    # Fetch lead counts in one query
    lead_counts = (
        queryset.filter(created_at__year__in=[y for y, _ in month_year_pairs], created_at__month__in=[m for _, m in month_year_pairs])
        .values("created_at__year", "created_at__month")
        .annotate(count=Count("id"))
    )

    # Convert query result to dictionary {(year, month): count}
    lead_counts_dict = {(entry["created_at__year"], entry["created_at__month"]): entry["count"] for entry in lead_counts}

    total_leads_last_12 = 0  # Total count for last 12 months
    total_leads_last_6 = 0  # Total count for last 6 months

    # Process results in a single loop
    for i in range(1, len(all_months)):  # Start from index 1 to skip previous_month
        current_month, current_year = all_months[i].split('-')
        current_year = int(current_year)
        current_month_digit = month_to_digit(current_month)

        previous_month, previous_year = all_months[i - 1].split('-')
        previous_year = int(previous_year)
        previous_month_digit = month_to_digit(previous_month)

        this_month_count = lead_counts_dict.get((current_year, current_month_digit), 0)
        last_month_count = lead_counts_dict.get((previous_year, previous_month_digit), 0)

        data["last_12_months"].append({
            "month": current_month,
            "thisMonth": this_month_count,
            "lastMonth": last_month_count
        })

        total_leads_last_12 += this_month_count  # Update total count for last 12 months

    # Extract last 6 months from last_12_months list
    data["last_6_months"] = data["last_12_months"][-6:]

    # Calculate total leads for the last 6 months
    total_leads_last_6 = sum(entry["thisMonth"] for entry in data["last_6_months"])

    # Add total leads count to the data dictionary
    data["total_leads_last_12_months"] = total_leads_last_12
    data["total_leads_last_6_months"] = total_leads_last_6

    return data, queryset


def calculate_last_days(queryset, days_and_months, data):
    # Get the list of dates
    date_list = days_and_months["last_30_days"][:]  # Copy to avoid modifying the original
    previous_date = get_previous_date(date_list[0])  # Get the previous date
    date_list.insert(0, previous_date)  # Add the previous date at the start

    # Count leads per date in a single query
    lead_counts = (
        queryset.filter(created_at__date__in=date_list)
        .values("created_at__date")
        .annotate(count=Count("id"))
    )

    # Convert result to dictionary format { "YYYY-MM-DD": count }
    lead_counts_dict = {str(entry["created_at__date"]): entry["count"] for entry in lead_counts}

    total_leads_last_30 = 0  # Total count for last 30 days
    total_leads_last_7 = 0  # Total count for last 7 days

    # Process results
    for i, date in enumerate(date_list):
        if date == previous_date:  # **Skip the previous_date**
            continue

        this_day_count = lead_counts_dict.get(date, 0)
        last_day_count = lead_counts_dict.get(date_list[i - 1], 0) if i > 0 else 0  # Get previous day's count

        data["last_30_days"].append({
            "day": date,
            "thisDay": this_day_count,
            "lastDay": last_day_count
        })

        total_leads_last_30 += this_day_count  # Update total count for last 30 days

    # Extract last 7 days from last_30_days list
    data["last_7_days"] = data["last_30_days"][-7:]

    # Calculate total leads for the last 7 days
    total_leads_last_7 = sum(entry["thisDay"] for entry in data["last_7_days"])

    # Add total leads count to the data dictionary
    data["total_leads_last_30_days"] = total_leads_last_30
    data["total_leads_last_7_days"] = total_leads_last_7

    return data
