import json
from ..models import Stage
from core.utils.notification_utils import notification_obj
import random
import string
from datetime import datetime
from django.db import IntegrityError

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


def get_default_lead_stage(business_id):
    return Stage.objects.filter(business_id=business_id, is_default=True, is_active=True, type="open").first()

def get_default_lead_stage_by_priority(business_id):
    return Stage.objects.filter(business_id=business_id, is_active=True, type="open").order_by('priority').first()


def generate_unique_code(model, prefix="LD"):
    for _ in range(5):  # retry limit
        date_part = datetime.now().strftime("%y%m%d")
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        code = f"{prefix}-{date_part}-{random_part}"

        if not model.objects.filter(code=code).exists():
            return code

    raise Exception("Unable to generate unique lead code")