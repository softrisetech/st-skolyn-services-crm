import json
from django.conf import settings
from rest_framework import status
from django.utils import timezone
from django.http import JsonResponse
# from pytz import timezone as pytz_timezone
from django.utils.deprecation import MiddlewareMixin

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