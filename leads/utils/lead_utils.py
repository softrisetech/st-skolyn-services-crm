import json
from core.utils.notification_utils import notification_obj

def handle_email_trigger(request, lead, notifications):
    if lead.p_email is not None:
        data = request.data
        branch = json.loads(data.get("branch"))
        notification_to_send = [lead.p_email]
        type_id = data.get('type_id')
        notifications.append(notification_obj(
            "trigger_email",
            notification_to_send,
            {
                'business_id': lead.business_id,
                'branch_id': lead.branch_id,
                'branch_name': branch["name"],
                'branch_contact_number': branch["contact_number"],
                'branch_address': branch["address"],
                'object_id': lead.stage_id,
                'sub_object_id': type_id,
                'student_name': lead.name,
                'parent_name': lead.p_name
            }
        ))