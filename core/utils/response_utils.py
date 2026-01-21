from rest_framework.response import Response
from rest_framework import status

def success_response(message_key, status_code=status.HTTP_200_OK, data = [], other = []):
    response = {
        'status': True,
        'status_code': status_code,
        'message': message_key,
        'data': data,
        'other': other
    }
    return Response(response)

def error_response(message_key, status_code=status.HTTP_400_BAD_REQUEST, errors = []):
    response = {
        'status': False,
        'status_code': status_code,
        'message': message_key,
        'errors': errors
    }
    return Response(response)
