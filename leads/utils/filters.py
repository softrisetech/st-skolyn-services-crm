from django.db.models import Q
from datetime import datetime, time
from core.utils.date_time_converter import DateTimeConverter

def search_filter(queryset, filters):
    search_query = filters.get('search')
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(p_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(p_email__icontains=search_query) |
            Q(p_contact_number__icontains=search_query)
        )

    return queryset

def filter_by_branches(queryset, filters):
    branches = filters.getlist('branches[]') or filters.get('branches')
    if branches:
        # Ensure branches is a list; if it's a single string, convert it into a list
        if isinstance(branches, str):
            branches = branches.split(',')  # Convert to a list after stripping spaces
        elif isinstance(branches, list):
            branches = [b.strip() for b in branches if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if branches:
            queryset = queryset.filter(branch_id__in=branches)

    return queryset

def filter_by_created_by(queryset, filters):
    created_bys = filters.getlist('created_bys[]') or filters.get('created_bys')
    if created_bys:
        # Ensure created_bys is a list; if it's a single string, convert it into a list
        if isinstance(created_bys, str):
            created_bys = [created_bys.strip()]  # Convert to a list after stripping spaces
        elif isinstance(created_bys, list):
            created_bys = [b.strip() for b in created_bys if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if created_bys:
            queryset = queryset.filter(created_by__in=created_bys)

    return queryset

def filter_by_assigned_to(queryset, filters):
    assigned_tos = filters.getlist('assigned_tos[]') or filters.get('assigned_tos')
    if assigned_tos:
        # Ensure assigned_tos is a list; if it's a single string, convert it into a list
        if isinstance(assigned_tos, str):
            assigned_tos = [assigned_tos.strip()]  # Convert to a list after stripping spaces
        elif isinstance(assigned_tos, list):
            assigned_tos = [b.strip() for b in assigned_tos if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if assigned_tos:
            queryset = queryset.filter(assigned_to__in=assigned_tos)

    return queryset

def filter_by_mediums(queryset, filters):
    mediums = filters.getlist('mediums[]') or filters.get('mediums')
    if mediums:
        # Ensure mediums is a list; if it's a single string, convert it into a list
        if isinstance(mediums, str):
            mediums = [mediums.strip()]  # Convert to a list after stripping spaces
        elif isinstance(mediums, list):
            mediums = [b.strip() for b in mediums if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if mediums:
            queryset = queryset.filter(medium__in=mediums)

    return queryset

def filter_by_sources(queryset, filters):
    sources = filters.getlist('sources[]') or filters.get('sources')
    if sources:
        # Ensure sources is a list; if it's a single string, convert it into a list
        if isinstance(sources, str):
            sources = sources.split(',')  # Convert to a list after stripping spaces
        elif isinstance(sources, list):
            sources = [b.strip() for b in sources if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if sources:
            queryset = queryset.filter(source__in=sources)

    return queryset

def filter_by_stages(queryset, filters):
    stages = filters.getlist('stages[]') or filters.get('stages')
    if stages:
        # Ensure stages is a list; if it's a single string, convert it into a list
        if isinstance(stages, str):
            stages = stages.split(',')  # Convert to a list after stripping spaces
        elif isinstance(stages, list):
            stages = [b.strip() for b in stages if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if stages:
            queryset = queryset.filter(stage__in=stages)

    return queryset

def filter_by_tags(queryset, filters):
    tags = filters.getlist('tags[]') or filters.get('tags')
    if tags:
        # Ensure tags is a list; if it's a single string, convert it into a list
        if isinstance(tags, str):
            tags = tags.split(',')  # Convert to a list after stripping spaces
        elif isinstance(tags, list):
            tags = [b.strip() for b in tags if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if tags:
            queryset = queryset.filter(tag__in=tags)

    return queryset

def filter_by_date_range(queryset, filters):
    created_from = filters.get("created_from")
    created_to = filters.get("created_to")

    if created_from:
        created_from = DateTimeConverter.to_utc_date(created_from, filters.get("auth_timezone"))

    if created_to:
        created_to = DateTimeConverter.to_utc_date(created_to, filters.get("auth_timezone"))

    if created_from and created_to:
        created_to = datetime.strptime(created_to, "%Y-%m-%d").date()
        created_to = datetime.combine(created_to, time.max)
        queryset = queryset.filter(created_at__gte=created_from, created_at__lte=created_to)
    elif created_from:
        queryset = queryset.filter(created_at__date=created_from)
    elif created_to:
        queryset = queryset.filter(created_at__date=created_to)

    return queryset

def filter_by_converted(queryset, filters):
    is_converted = filters.get('is_converted')
    if is_converted:
        converted = int(is_converted)
        queryset = queryset.filter(converted=converted)

    return queryset

def filter_by_sessions(queryset, filters):
    sessions = filters.getlist('sessions[]') or filters.get('sessions')
    if sessions:
        # Ensure sessions is a list; if it's a single string, convert it into a list
        if isinstance(sessions, str):
            sessions = sessions.split(',')  # Convert to a list after stripping spaces
        elif isinstance(sessions, list):
            sessions = [b.strip() for b in sessions if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if sessions:
            queryset = queryset.filter(session_id__in=sessions)

    return queryset

def filter_by_generated(queryset, filters):
    is_generated = filters.get('is_generated')
    if is_generated:
        is_generated = int(is_generated)
        queryset = queryset.filter(is_generated=is_generated)

    return queryset

def filter_by_active(queryset, filters):
    is_active = filters.get('is_active')
    if is_active:
        queryset = queryset.filter(is_active=is_active)

    return queryset

def filter_by_type(queryset, filters):
    type = filters.get('type')
    if type:
        queryset = queryset.filter(type=type)

    return queryset

def filter_by_priority(queryset, filters):
    priority = filters.get('priority')
    if priority:
        queryset = queryset.filter(priority=priority)

    return queryset

def filter_by_default(queryset, filters):
    is_default = filters.get('is_default')
    if is_default:
        queryset = queryset.filter(is_default=is_default)

    return queryset

def filter_by_start_and_end_date(queryset, filters):
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    timezone = filters.get("auth_timezone")

    if start_date:
        start_date = DateTimeConverter.to_utc_date(start_date, timezone)

    if end_date:
        end_date = DateTimeConverter.to_utc_date(end_date, timezone)

    if start_date and end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        end_date = datetime.combine(end_date, time.max)
        queryset = queryset.filter(date__gte=start_date, date__lte=end_date)
    elif start_date:
        queryset = queryset.filter(date__date=start_date)
    elif end_date:
        queryset = queryset.filter(date__date=end_date)

    return queryset

def filter_by_duration(queryset, filters):
    duration = filters.get('duration')
    if duration:
        queryset = queryset.filter(duration=duration)

    return queryset

def filter_by_followup_bys(queryset, filters):
    follow_up_bys = filters.getlist('follow_up_bys[]') or filters.get('follow_up_bys')
    if follow_up_bys:
        # Ensure follow_up_bys is a list; if it's a single string, convert it into a list
        if isinstance(follow_up_bys, str):
            follow_up_bys = [follow_up_bys.strip()]  # Convert to a list after stripping spaces
        elif isinstance(follow_up_bys, list):
            follow_up_bys = [b.strip() for b in follow_up_bys if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if follow_up_bys:
            queryset = queryset.filter(follow_up_by__in=follow_up_bys)

    return queryset

def filter_by_model_type(queryset, filters):
    model_type = filters.get('model_type')
    if model_type:
        queryset = queryset.filter(model_type=model_type)

    return queryset