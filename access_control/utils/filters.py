def filter_by_module(querset, filters):
    module = filters.get('module_id')
    if module:
        queryset = queryset.filter(module=module)

    return querset

def filter_by_type(queryset, filters):
    type = filters.get('type')
    if type:
        queryset = queryset.filter(type=type)

    return queryset

def filter_by_active(queryset, filters):
    is_active = filters.get('is_active')
    if is_active:
        queryset = queryset.filter(is_active=is_active)

    return queryset