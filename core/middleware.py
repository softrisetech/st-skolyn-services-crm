import json
from django.conf import settings
from rest_framework import status
from django.utils import timezone
from django.http import JsonResponse
# from pytz import timezone as pytz_timezone
from django.utils.deprecation import MiddlewareMixin
from threading import local

# Thread-local storage
_thread_locals = local()


def get_current_request():
    """Helper function to get current request from thread local"""
    return getattr(_thread_locals, 'request', None)


class ActivityLogMiddleware:
    """
    Middleware that extracts auth_id and business_id from request
    and stores them in thread local for activity logging
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract auth_id and business_id
        auth_id = None
        business_id = None
        
        # Method 1: From request body (POST/PUT/PATCH)
        if request.method in ['POST', 'PUT', 'PATCH'] and request.content_type == 'application/json':
            try:
                # Parse JSON body
                body = request.body.decode('utf-8')
                if body:
                    data = json.loads(body)
                    auth_id = data.get('auth_id')
                    business_id = data.get('auth_business_id')
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        
        # Method 2: From request attributes (set by other middleware/decorators)
        if not auth_id and hasattr(request, 'auth_id'):
            auth_id = request.auth_id
        
        if not business_id and hasattr(request, 'auth_business_id'):
            business_id = request.auth_business_id
        
        # Method 3: From GET/POST params
        if not auth_id:
            auth_id = request.GET.get('auth_id') or request.POST.get('auth_id')
        
        if not business_id:
            business_id = request.GET.get('auth_business_id') or request.POST.get('auth_business_id')
        
        # Method 4: From headers
        if not auth_id:
            auth_id = request.headers.get('X-Auth-Id') or request.headers.get('Auth-Id')
        
        if not business_id:
            business_id = request.headers.get('X-Business-Id') or request.headers.get('Business-Id')
        
        # Store in thread local (even if business_id is None)
        _thread_locals.request = request
        _thread_locals.auth_id = auth_id
        _thread_locals.business_id = business_id
        
        # Attach to request
        request.audit_auth_id = auth_id
        request.audit_business_id = business_id        
        # Process request
        response = self.get_response(request)
        
        # Clean up thread local
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        if hasattr(_thread_locals, 'auth_id'):
            del _thread_locals.auth_id
        if hasattr(_thread_locals, 'business_id'):
            del _thread_locals.business_id
        
        return response
class GatewayAuthorizationMiddleware:
    """
    Initialize the AccessKeyMiddleware with the given response handler.

    Args:
        get_response (callable): The next middleware or view in the chain
        that will process the request after this middleware.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exempt_routes = []
        current_route = request.path_info
        if current_route not in exempt_routes:
            access_key = request.headers.get("Access-Key", None)

            if access_key == None or access_key != getattr(settings, "ACCESS_KEY", None):
                response_data = {
                    "status": False,
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "message": "service_access_unauthorized",
                    "errors": [],
                }
                return JsonResponse(
                    response_data
                )

        return self.get_response(request)

class GlobalExceptionMiddleware(MiddlewareMixin):
    """
    Catches any unhandled exceptions that occur in the application and returns a
    custom JSON response with a 500 status code.

    Args:
        request (HttpRequest): The current request object
        exception (Exception): The exception that was raised

    Returns:
        JsonResponse: A JSON response with the error details
    """
    def process_exception(self, request, exception):
        # Log the exception (optional)
        print(f"Exception occurred: {exception}")

        # Customize the response for exceptions
        response_data = {
            "status": False,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": f"Crm Service Exception: {str(exception)}",
            "errors": [],
        }
        return JsonResponse(
            response_data
        )

# class TimezoneMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         user_timezone = request.GET.auth_timezone
#
#         # Set the user's time zone if available, otherwise use default (UTC)
#         if user_timezone:
#             try:
#                 tz = pytz_timezone(user_timezone)  # user_timezone should be a valid timezone string
#                 timezone.activate(tz)
#             except Exception:
#                 timezone.activate(pytz_timezone('UTC'))  # Fallback to UTC if invalid timezone
#         else:
#             timezone.activate(pytz_timezone('UTC'))  # Use UTC by default
#
#         response = self.get_response(request)
#         return response