from ..models import Export
import asyncio


def export_obj(type, req_data):
    return {
        "type": type,
        "ReqData": req_data
    }

async def export_entry(data):
    business_id = data.get("auth_business_id")
    created_by = data.get("auth_id")
    app_slug = data.get("app_slug")
    report_type = data.get("report_type")
    payload = dict(data) 

    entry = await asyncio.to_thread(
        Export.objects.create,
        business_id=business_id,
        app_slug=app_slug,
        type=report_type,
        status="pending",
        created_by=created_by,
        payload=payload,
        link=None,
        file_name=data.get("file_name"),   
    )
    return entry