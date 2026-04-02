from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q

from rest_framework.decorators import api_view

from ..models import Permission, RolePermission
from ..serializers import PermissionSerializer

from core.utils.response_utils import success_response, error_response
from core.utils.pagination_utils import CustomPagination

class PermissionListAPIView(APIView):

    pagination_class = CustomPagination

    def post(self, request):

        queryset = Permission.objects.all()
        filters = request.data


        if 'search' in filters:
            queryset = queryset.filter(
                # Q(name__icontains=filters['search']) |
                # Q(description__icontains=filters['search']) |
                # Q.url__icontains=filters['search'] |
                # Q.key__icontains=filters['search']
            )

        if 'module_id' in filters:
            queryset = queryset.filter(module=filters['module_id'])

        if 'type' in filters:
            queryset = queryset.filter(type=filters['type'])

        if 'is_active' in filters:
            queryset = queryset.filter(is_active=filters['is_active'])


        paginator = self.pagination_class()
        paginated = paginator.paginate_queryset(queryset, request)

        data = PermissionSerializer(paginated, many=True).data
        response = paginator.get_paginated_response(data)

        return success_response('record_fetched', status.HTTP_200_OK, response)


class PermissionRetrieveAPIView(APIView):

    def post(self, request, pk):

        module_id = request.data.get('module_id')

        permission = Permission.objects.filter(
            id=pk,
            module=module_id
        ).first()

        if not permission:
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

        data = PermissionSerializer(permission).data

        return success_response('record_fetched', status.HTTP_200_OK, data)


class PermissionCreateAPIView(APIView):

    def post(self, request):

        data = request.data.copy()

        module_id = data.get('module_id')
        permissions = data.get('permissions', [])

        for p in permissions:
            p['module'] = module_id


        serializer = PermissionSerializer(data=permissions, many=True)

        if serializer.is_valid():

            serializer.save()

            return success_response(
                'record_stored',
                status.HTTP_201_CREATED,
                serializer.data
            )

        return error_response(
            'invalid_data',
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            serializer.errors
        )

class PermissionUpdateAPIView(APIView):

    def post(self, request, pk):

        module_id = request.data.get('module_id')

        permission = Permission.objects.filter(
            id=pk,
            module=module_id
        ).first()

        if not permission:
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['module'] = module_id

        serializer = PermissionSerializer(
            instance=permission,
            data=data,
            partial=False
        )

        if serializer.is_valid():

            serializer.save()

            return success_response(
                'record_updated',
                status.HTTP_200_OK,
                serializer.data
            )

        return error_response(
            'invalid_data',
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            serializer.errors
        )

class PermissionDeleteAPIView(APIView):

    def post(self, request, pk):

        module_id = request.data.get('module_id')

        permission = Permission.objects.filter(
            id=pk,
            module=module_id
        ).first()

        if not permission:
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

        permission.delete()

        return success_response('record_deleted', status.HTTP_200_OK)


@api_view(['POST'])
def change_permission_status(request, pk):

    module_id = request.data.get('module_id')

    permission = Permission.objects.filter(
        id=pk,
        module=module_id
    ).first()

    if not permission:
        return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

    serializer = PermissionSerializer(
        instance=permission,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():

        serializer.save()

        return success_response(
            'record_updated',
            status.HTTP_200_OK,
            serializer.data
        )

    return error_response(
        'invalid_data',
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        serializer.errors
    )


@api_view(['POST'])
def get_role_based_permissions(request):
    data = request.data
    is_staff = data.get("auth_is_staff")
    if is_staff == "true" or is_staff == True:
        role_id = data.get("auth_role_id")
        role_permission_ids = RolePermission.objects.filter(role_id=role_id).values("permission_id")
        permissions = Permission.objects.filter(id__in=role_permission_ids)
    else:
        permissions = Permission.objects.all()

    permission_data = PermissionSerializer(permissions, many=True).data
    
    print("permission_data",permission_data)

    result = {}

    for permission in permission_data:
        module_slug = permission["module_obj"]["slug"]

        url = permission["url"] or ""
        frontend_url = permission["frontend_url"] or ""
        key = permission["key"] or ""

        if module_slug in result:
            if url:
                result[module_slug]["backend_url"].extend([u.strip() for u in url.split(",") if u.strip()])
            if frontend_url:
                result[module_slug]["frontend_url"].extend([u.strip() for u in frontend_url.split(",") if u.strip()])
            if key:
                result[module_slug]["key"].append(key)
        else:
            result[module_slug] = {
                "module_id": permission["module"],
                "backend_url": [u.strip() for u in url.split(",") if u.strip()] if url else [],
                "frontend_url": [u.strip() for u in frontend_url.split(",") if u.strip()] if frontend_url else [],
                "key": [key] if key else []
            }
            
        print("result",result)
        

        #remove duplicates
        for module_data in result.values():
            module_data["backend_url"] = list(set(module_data["backend_url"]))
            module_data["frontend_url"] = list(set(module_data["frontend_url"]))
            module_data["key"] = list(set(module_data["key"]))

    return success_response('record_fetched', status.HTTP_200_OK, result)

