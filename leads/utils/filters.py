from django.db.models import Q
from datetime import datetime, time
from core.utils.date_time_converter import DateTimeConverter
from django.db.models import Value
from django.db.models.functions import Concat, Coalesce

def _parse_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
    return None


def lead_search_filter(queryset, filters):
    search_query = filters.get('search')
    if search_query:
        queryset = queryset.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(contact_number__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(nic__icontains=search_query) |
            Q(gender__icontains=search_query) |
            Q(ethnicity__icontains=search_query) |
            Q(remarks__icontains=search_query) |
            Q(code__icontains=search_query)
        )

    return queryset

def lead_follow_up_search_filter(queryset, filters):
    search_query = filters.get('search')
    if search_query:
        queryset = queryset.filter(
            Q(follow_up_type__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    return queryset

def filter_by_lead_pre_requisite_search_filter(queryset, filters):
    search_query = filters.get('search')
    if search_query:
        queryset = queryset.filter(
            Q(board_name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(program__icontains=search_query) |
            Q(courses__course_name__icontains=search_query) |
            Q(institute__name__icontains=search_query)
        )

    return queryset


def filter_by_branches(queryset, filters):
    branch_ids = filters.get('branch_ids')
    if branch_ids:
        # Ensure branch_ids is a list; if it's a single string, convert it into a list
        if isinstance(branch_ids, str):
            branch_ids = branch_ids.split(',')  # Convert to a list after stripping spaces
        elif isinstance(branch_ids, list):
            branch_ids = [b.strip() for b in branch_ids if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if branch_ids:
            queryset = queryset.filter(branch_id__in=branch_ids)

    return queryset

def filter_by_created_by(queryset, filters):
    created_bys = filters.get('created_bys')
    if created_bys:
        # Ensure created_bys is a list; if it's a single string, convert it into a list
        if isinstance(created_bys, str):
            created_bys = created_bys.split(',')  # Convert to a list after stripping spaces
        elif isinstance(created_bys, list):
            created_bys = [b.strip() for b in created_bys if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if created_bys:
            queryset = queryset.filter(created_by__in=created_bys)

    return queryset

def filter_by_assigned_to(queryset, filters):
    assigned_tos = filters.get('assigned_tos')
    if assigned_tos:
        # Ensure assigned_tos is a list; if it's a single string, convert it into a list
        if isinstance(assigned_tos, str):
            assigned_tos = assigned_tos.split(',')  # Convert to a list after stripping spaces
        elif isinstance(assigned_tos, list):
            assigned_tos = [b.strip() for b in assigned_tos if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if assigned_tos:
            queryset = queryset.filter(assigned_to__in=assigned_tos)

    return queryset

def filter_by_countries(queryset, filters):
    countries = filters.get('countries')
    if countries:
        # Ensure countries is a list; if it's a single string, convert it into a list
        if isinstance(countries, str):
            countries = countries.split(',')  # Convert to a list after stripping spaces
        elif isinstance(countries, list):
            countries = [b.strip() for b in countries if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if countries:
            queryset = queryset.filter(country_id__in=countries)

    return queryset

def filter_by_states(queryset, filters):
    states = filters.get('states')
    if states:
        # Ensure states is a list; if it's a single string, convert it into a list
        if isinstance(states, str):
            states = states.split(',')  # Convert to a list after stripping spaces
        elif isinstance(states, list):
            states = [b.strip() for b in states if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if states:
            queryset = queryset.filter(state_id__in=states)

    return queryset


def filter_by_cities(queryset, filters):
    cities = filters.get('cities')
    if cities:
        # Ensure cities is a list; if it's a single string, convert it into a list
        if isinstance(cities, str):
            cities = cities.split(',')  # Convert to a list after stripping spaces
        elif isinstance(cities, list):
            cities = [b.strip() for b in cities if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if cities:
            queryset = queryset.filter(city_id__in=cities)

    return queryset

def filter_by_classes(queryset, filters):
    classes = filters.get('classes')
    if classes:
        # Ensure classes is a list; if it's a single string, convert it into a list
        if isinstance(classes, str):
            classes = classes.split(',')  # Convert to a list after stripping spaces
        elif isinstance(classes, list):
            classes = [b.strip() for b in classes if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if classes:
            queryset = queryset.filter(class_id__in=classes)

    return queryset


def filter_by_mediums(queryset, filters):
    mediums = filters.get('mediums')
    if mediums:
        # Ensure mediums is a list; if it's a single string, convert it into a list
        if isinstance(mediums, str):
            mediums = mediums.split(',')  # Convert to a list after stripping spaces
        elif isinstance(mediums, list):
            mediums = [b.strip() for b in mediums if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if mediums:
            queryset = queryset.filter(medium__in=mediums)

    return queryset

def filter_by_sources(queryset, filters):
    sources = filters.get('sources')
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
    stages = filters.get('stages')
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
    tags = filters.get('tags')
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

def filter_by_teams(queryset, filters):
    teams = filters.get('teams')
    if teams:
        # Ensure teams is a list; if it's a single string, convert it into a list
        if isinstance(teams, str):
            teams = teams.split(',')  # Convert to a list after stripping spaces
        elif isinstance(teams, list):
            teams = [b.strip() for b in teams if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if teams:
            queryset = queryset.filter(team__in=teams)

    return queryset

def filter_by_campaigns(queryset, filters):
    campaigns = filters.get('campaigns')
    if campaigns:
        # Ensure campaigns is a list; if it's a single string, convert it into a list
        if isinstance(campaigns, str):
            campaigns = campaigns.split(',')  # Convert to a list after stripping spaces
        elif isinstance(campaigns, list):
            campaigns = [b.strip() for b in campaigns if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if campaigns:
            queryset = queryset.filter(campaign__in=campaigns)

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

def filter_by_is_father_applicable(queryset, filters):
    is_father_applicable = _parse_bool(filters.get('is_father_applicable'))
    if is_father_applicable is not None:
        queryset = queryset.filter(is_father_applicable=is_father_applicable)
    return queryset


def filter_by_is_mother_applicable(queryset, filters):
    is_mother_applicable = _parse_bool(filters.get('is_mother_applicable'))
    if is_mother_applicable is not None:
        queryset = queryset.filter(is_mother_applicable=is_mother_applicable)
    return queryset

def filter_by_sessions(queryset, filters):
    session_ids = filters.get('session_ids')
    if session_ids:
        # Ensure session_ids is a list; if it's a single string, convert it into a list
        if isinstance(session_ids, str):
            session_ids = session_ids.split(',')  # Convert to a list after stripping spaces
        elif isinstance(session_ids, list):
            session_ids = [b.strip() for b in session_ids if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if session_ids:
            queryset = queryset.filter(session_id__in=session_ids)

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


def filter_by_priorities(queryset, filters):
    priorities = filters.get('priorities')
    if priorities:
        # Ensure priorities is a list; if it's a single string, convert it into a list
        if isinstance(priorities, str):
            priorities = priorities.split(',')  # Convert to a list after stripping spaces
        elif isinstance(priorities, list):
            priorities = [b.strip() for b in priorities if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if priorities:
            queryset = queryset.filter(priority__in=priorities)

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
        start_date = DateTimeConverter.to_utc_range(start_date, timezone, is_end=False)

    if end_date:
        end_date = DateTimeConverter.to_utc_range(end_date, timezone, is_end=True)

    if start_date and end_date:
        queryset = queryset.filter(date_time__gte=start_date, date_time__lte=end_date)
    elif start_date:
        queryset = queryset.filter(date_time__gte=start_date)
    elif end_date:
        queryset = queryset.filter(date_time__lte=end_date)

    return queryset


def filter_by_follow_up_types(queryset, filters):
    follow_up_types = filters.get('follow_up_types')
    if follow_up_types:
        # Ensure follow_up_types is a list; if it's a single string, convert it into a list
        if isinstance(follow_up_types, str):
            follow_up_types = follow_up_types.split(',')  # Convert to a list after stripping spaces
        elif isinstance(follow_up_types, list):
            follow_up_types = [b.strip() for b in follow_up_types if b.strip()]  # Remove empty values

        # Apply filter if the list is not empty
        if follow_up_types:
            queryset = queryset.filter(follow_up_type__in=follow_up_types)

    return queryset

def filter_by_done(queryset, filters):
    is_done = filters.get('is_done')
    if is_done is not None:
        is_done = int(is_done)
        queryset = queryset.filter(is_done=is_done)

    return queryset

def filter_by_duration(queryset, filters):
    duration = filters.get('duration')
    if duration:
        queryset = queryset.filter(duration=duration)

    return queryset

def filter_by_created_bys(queryset, filters):
    created_bys = filters.get('created_bys')
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

def filter_by_model_type(queryset, filters):
    model_type = filters.get('model_type')
    if model_type:
        queryset = queryset.filter(model_type=model_type)

    return queryset


def filter_by_sort_order(queryset, filters):
    sort_by = filters.get('sort_by')
    sort_order = filters.get('sort_order', 'asc')

    full_name_mappings = {
        "full_name": ("first_name", "last_name"),
        "father_full_name": ("father_first_name", "father_last_name"),
        "mother_full_name": ("mother_first_name", "mother_last_name"),
    }

    # Handle virtual full name fields
    if sort_by in full_name_mappings:
        first_field, last_field = full_name_mappings[sort_by]

        queryset = queryset.annotate(
            **{
                sort_by: Concat(
                    Coalesce(first_field, Value("")),
                    Value(" "),
                    Coalesce(last_field, Value(""))
                )
            }
        )

    # Apply descending order
    if sort_order == "desc":
        sort_by = f"-{sort_by}"

    if sort_by:
        queryset = queryset.order_by(sort_by)

    return queryset

def filter_by_integrate_with_google_calendar(queryset, filters):
    integrate_with_google_calendar = filters.get('integrate_with_google_calendar')
    if integrate_with_google_calendar:
        queryset = queryset.filter(integrate_with_google_calendar=integrate_with_google_calendar)

    return queryset