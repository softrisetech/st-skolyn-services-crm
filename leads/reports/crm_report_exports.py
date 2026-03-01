
from report_export.utils.constants import constants
from report_export.utils.export_helpers import export_entry, export_obj
import asyncio
from core.utils.response_utils import success_response, error_response
from rest_framework import status
from core.utils.decorators import access_control_middleware
from rest_framework.decorators import api_view

@api_view(['POST'])
@access_control_middleware
def export_high_priority_no_followup(request):
    data = request.data.copy()
    try:
        data["report_type"] = constants()["report_type"]["crm"]["high_priority_no_followup"]
        entry = asyncio.run(export_entry(data))
        data["export_entry_id"] = entry.id
        result = export_obj(data["report_type"], data)
        return success_response('record_fetched', status.HTTP_200_OK, result)
    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['POST'])
@access_control_middleware
def export_no_followup_leads(request):
    data = request.data.copy()
    try:
        data["report_type"] = constants()["report_type"]["crm"]["no_followup_leads"]
        entry = asyncio.run(export_entry(data))
        data["export_entry_id"] = entry.id
        result = export_obj(data["report_type"], data)
        return success_response('record_fetched', status.HTTP_200_OK, result)
    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@access_control_middleware
def export_upcoming_followup_leads(request):
    data = request.data.copy()
    try:
        data["report_type"] = constants()["report_type"]["crm"]["upcoming_followup_leads"]
        entry = asyncio.run(export_entry(data))
        data["export_entry_id"] = entry.id
        result = export_obj(data["report_type"], data)
        return success_response('record_fetched', status.HTTP_200_OK, result)
    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@access_control_middleware
def export_overdue_followup_leads(request):
    data = request.data.copy()
    try:
        data["report_type"] = constants()["report_type"]["crm"]["overdue_followup_leads"]
        entry = asyncio.run(export_entry(data))
        data["export_entry_id"] = entry.id
        result = export_obj(data["report_type"], data)
        return success_response('record_fetched', status.HTTP_200_OK, result)
    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@access_control_middleware
def export_lost_leads(request):
    data = request.data.copy()
    try:
        data["report_type"] = constants()["report_type"]["crm"]["lost_leads"]
        entry = asyncio.run(export_entry(data))
        data["export_entry_id"] = entry.id
        result = export_obj(data["report_type"], data)
        return success_response('record_fetched', status.HTTP_200_OK, result)
    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)