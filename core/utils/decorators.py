import re
from functools import wraps
from rest_framework import status
from access_control.models import Permission, RolePermission
from core.utils.response_utils import error_response
from core.utils.helpers import check_if_user_is_staff

def access_control_middleware(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # Support both CBV (self, request, ...) and FBV (request, ...)
        if hasattr(args[0], 'method'):
            request = args[0]  # FBV
        else:
            request = args[1]  # CBV

        if request.content_type == "application/json":
            data = request.data
        else:
            data = request.GET or request.POST

        is_staff = check_if_user_is_staff(data)
        if is_staff not in [True, "true"]:
            return view_func(*args, **kwargs)

        url = get_current_url(request)
        permission = Permission.objects.filter(url__icontains=url.rstrip('/')).first()

        if not permission:
            return view_func(*args, **kwargs)

        role_id = data.get("auth_role_id")
        readable_url = get_readable_url(url)

        if not role_id:
            return error_response(
                f'Access denied: no role assigned to perform "{permission.name}" on "{readable_url}"',
                status.HTTP_403_FORBIDDEN
            )

        if not RolePermission.objects.filter(role_id=role_id, permission_id=permission.id).exists():
            return error_response(
                f'Access denied: your role does not have "{permission.name}" permission for "{readable_url}"',
                status.HTTP_403_FORBIDDEN
            )

        return view_func(*args, **kwargs)
    return wrapper


def get_current_url(request):
    current_url = request.path_info

    if current_url != "/":
        # Strip BOTH leading and trailing slashes for consistency
        current_url = current_url.strip('/')

    # Normalize UUID segments regardless of trailing slash presence
    current_url = re.sub(
        r'/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})(/|$)',
        r'/{id}\2',
        current_url
    )

    return current_url


def get_readable_url(url):
    segment = url.lstrip('/').rstrip('/').split('/')[0]
    return segment.replace('-', ' ').replace('_', ' ').title()