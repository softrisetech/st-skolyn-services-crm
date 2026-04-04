import re
import json
from rest_framework import status
from django.http import JsonResponse
from django.http.multipartparser import MultiPartParser
from access_control.models import Permission, RolePermission

class AccessControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Normalize URL (remove UUID at the end and replace with {id})
        current_url = request.path_info
        if current_url != "/":  # Keep the slash if it's the root URL
            current_url = current_url.lstrip('/').rstrip('/')

        # Normalize URL (remove UUID and replace with {id})
        current_url = re.sub(r'/(?P<id>[0-9a-fA-F-]{36})$', '/{id}', current_url)
        body_data = {}

        # Read and cache body only once
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            if not hasattr(request, "_cached_body"):  # Prevent multiple reads
                request._cached_body = request.body  # Store body for later use

            if request.content_type.startswith("application/json"):
                try:
                    body = request._cached_body.decode("utf-8")
                    body_data = json.loads(body) if body else {}
                except json.JSONDecodeError:
                    return JsonResponse({"error": "Invalid JSON format"}, status=400)

            elif request.content_type.startswith("multipart/form-data"):
                if request.method in ["PUT", "DELETE", "PATCH"]:
                    parser = MultiPartParser(request.META, request, request.upload_handlers)
                    data, files = parser.parse()
                    body_data = {**data.dict(), **{k: v.name for k, v in files.items()}}
                else:
                    body_data = request.POST.dict()

        elif request.method == "GET":
            body_data = request.GET.dict()

        # Attach parsed data to request
        request.body_data = body_data  # Use `request.body_data` instead of re-reading `request.body`

        response = self.get_response(request)

        # Authorization check
        if body_data.get("auth_is_staff") != "true":
            return response

        role_id = body_data.get("role_id")
        #check if permission exists in system other wise by pass the middleware
        permission = Permission.objects.filter(url=current_url).first()
        if not permission:
            return self.get_response(request)

        if not role_id:
            return JsonResponse({
                "status": False,
                "status_code": status.HTTP_403_FORBIDDEN,
                "message": "permission_denied",
                "errors": {"current_url": current_url}
            })

        if not RolePermission.objects.filter(role_id=role_id, permission_id=permission.id).exists():
            return JsonResponse({
                "status": False,
                "status_code": status.HTTP_403_FORBIDDEN,
                "message": "permission_denied",
                "errors": {"current_url": current_url}
            })

        return response
