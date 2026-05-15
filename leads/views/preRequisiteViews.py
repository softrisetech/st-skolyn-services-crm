from rest_framework import status
from ..serializers import PreRequisiteSerializer, PreRequisiteCourseSerializer
from rest_framework.decorators import APIView
from ..models import PreRequisite, Lead, Institute, PreRequisiteCourse
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from core.utils.pagination_utils import CustomPagination
from core.utils.decorators import access_control_middleware
from core.utils.date_time_converter import DateTimeConverter
from core.utils.response_utils import success_response, error_response
from core.utils.notification_utils import notification, notification_obj
from django.db import transaction
from django.utils import timezone
from ..utils.filters import (
    filter_by_lead_pre_requisite_search_filter,
    filter_by_institutes,
    filter_by_sort_order
)


def __queryset(business_id, lead_id):
    return PreRequisite.objects.filter(business_id=business_id, lead_id=lead_id)


def __apply_filters(queryset, filters):
    queryset = filter_by_lead_pre_requisite_search_filter(queryset, filters)
    queryset = filter_by_institutes(queryset, filters)
    queryset = filter_by_sort_order(queryset, filters)
    return queryset

@api_view(['POST'])
@access_control_middleware
def get_lead_pre_requisites(request, lead_id):
    data = request.data
    timezone = data.get("auth_timezone")
    business_id = data.get('auth_business_id')

    lead = Lead.objects.filter(id=lead_id, business_id=business_id).first()
    if not lead:
        return error_response('lead_not_found', status.HTTP_404_NOT_FOUND)

    queryset = __queryset(business_id, lead_id)
    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = PreRequisiteSerializer(paginated_queryset, many=True).data
    for data in serialized_data:
        data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
        data["updated_at"] = DateTimeConverter.from_utc_datetime(data["updated_at"], timezone)

    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)
    

@api_view(['POST'])
@access_control_middleware
def store_lead_pre_requisite(request, lead_id):
    data = request.data.copy()
    data['business_id'] = request.data.get('auth_business_id')

    lead = Lead.objects.filter(id=lead_id, business_id=data['business_id']).first()
    if not lead:
        return error_response('lead_not_found', status.HTTP_404_NOT_FOUND)
    
    institute = Institute.objects.filter(id=data.get('institute'), business_id=data['business_id']).first()
    if not institute:
        return error_response('institute_not_found', status.HTTP_404_NOT_FOUND)

    data['lead'] = lead.id
    serializer = PreRequisiteSerializer(data=data)

    if not serializer.is_valid():
        return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    with transaction.atomic():

        prerequisite = serializer.save()

        courses = data.get('courses', [])
        if courses:
            success, errors = store_pre_requisite_courses(data['business_id'], lead.id, prerequisite.id, courses)
            if not success:
                transaction.set_rollback(True)
                return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, errors)

    return success_response('record_stored', status.HTTP_201_CREATED, serializer.data)

@api_view(['POST'])
@access_control_middleware
def update_lead_pre_requisite(request, lead_id, pk):
    data = request.data.copy()
    business_id = request.data.get('auth_business_id')
    data['business_id'] = business_id

    pre_requisite = PreRequisite.objects.filter(
        id=pk,
        business_id=business_id,
        lead_id=lead_id
    ).first()

    if not pre_requisite:
        return error_response('pre_requisite_not_found', status.HTTP_404_NOT_FOUND)
    
    institute = Institute.objects.filter(id=data.get('institute'), business_id=data['business_id']).first()
    if not institute:
        return error_response('institute_not_found', status.HTTP_404_NOT_FOUND)

    data['lead'] = pre_requisite.lead_id
    serializer = PreRequisiteSerializer(instance=pre_requisite, data=data, partial=False)

    if not serializer.is_valid():
        return error_response('record_update_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    with transaction.atomic():

        pre_requisite = serializer.save()

        courses = data.get('courses', [])
        if courses:
            pre_requisite.courses.all().update(deleted_at=timezone.now())
            success, errors = store_pre_requisite_courses(data['business_id'], pre_requisite.lead_id, pre_requisite.id, courses)

            if not success:
                transaction.set_rollback(True)
                return error_response('record_updation_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, errors)

    return success_response('record_updated', status.HTTP_200_OK, serializer.data)


@api_view(['POST'])
@access_control_middleware
def delete_lead_pre_requisite(request, lead_id, pk):
    business_id = request.data.get('auth_business_id')
    pre_requisite = PreRequisite.objects.filter(id=pk, business_id=business_id, lead_id=lead_id).first()
    if not pre_requisite:
        return error_response('pre_requisite_not_found', status.HTTP_404_NOT_FOUND)
    
    pre_requisite.courses.all().update(deleted_at=timezone.now())
    pre_requisite.delete()
    return success_response('record_deleted', status.HTTP_200_OK)


def store_pre_requisite_courses(business_id, lead_id, prerequisite_id, courses):
    course_objects = []

    for course in courses:
        course_data = {
            'business_id': business_id,
            'lead': lead_id,
            'prerequisite': prerequisite_id,
            'course_name': course.get('course_name'),
            'max_marks': course.get('max_marks'),
            'passing_marks': course.get('passing_marks'),
            'marks_in_percentage': course.get('marks_in_percentage'),
            'is_mandatory': course.get('is_mandatory', False)
        }

        serializer = PreRequisiteCourseSerializer(data=course_data)

        if not serializer.is_valid():
            return False, serializer.errors

        course_objects.append(
            PreRequisiteCourse(**serializer.validated_data)
        )

    if course_objects:
        PreRequisiteCourse.objects.bulk_create(course_objects)

    return True, None