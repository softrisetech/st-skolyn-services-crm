from django.db.models import Q
from datetime import datetime, time
from django.utils.dateparse import parse_date


def export_search_filter(queryset, filters):
    search = filters.get("search")
    if search:
        queryset = queryset.filter(
            Q(app_slug__icontains=search)
            | Q(type__icontains=search)
            | Q(status__icontains=search)
        )
    return queryset


def filter_export_by_status(queryset, filters):
    status = filters.get("status")
    if status:
        queryset = queryset.filter(status=status)
    return queryset


def filter_export_by_type(queryset, filters):
    type_ = filters.get("type")
    if type_:
        queryset = queryset.filter(type=type_)
    return queryset

def filter_export_by_file_name(queryset, filters):
    file_name = filters.get("file_name")

    if file_name:
        queryset = queryset.filter(
            Q(file_name__icontains=file_name)
        )

    return queryset

def filter_export_by_app_slug(queryset, filters):
    app_slug = filters.get("app_slug")
    if app_slug:
        queryset = queryset.filter(app_slug=app_slug)
    return queryset


def filter_export_by_created_by(queryset, filters):
    created_by = filters.get("created_by")
    if created_by:
        if isinstance(created_by, list):
            queryset = queryset.filter(created_by__in=created_by)
        else:
            queryset = queryset.filter(created_by__in=str(created_by).split(","))
    return queryset


def filter_export_by_date_range(queryset, filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    if from_date:
        queryset = queryset.filter(
            updated_at__gte=datetime.combine(parse_date(from_date), time.min)
        )
    if to_date:
        queryset = queryset.filter(
            updated_at__lte=datetime.combine(parse_date(to_date), time.max)
        )
    return queryset


def filter_by_sort_order(queryset, filters):
    sort_by = filters.get('sort_by')  # Default sort field
    sort_order = filters.get('sort_order')

    if sort_by:
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'
        queryset = queryset.order_by(sort_by)

    return queryset