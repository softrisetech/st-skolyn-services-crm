import json
import random
import string
import base64
from ..models import Stage
from datetime import datetime
from django.db import IntegrityError
from core.utils.notification_utils import notification_obj
from core.utils.date_time_converter import DateTimeConverter


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



def encrypt_business_id(business_id):
    return base64.urlsafe_b64encode(str(business_id).encode()).decode()

def decrypt_business_id(encrypted_id):
    try:
        return base64.urlsafe_b64decode(encrypted_id.encode()).decode()
    except Exception:
        return None
    
def handle_lead_email_notifications(data, user_timezone, sender_keys, email_notifications, trigger, lead, stage_reason=None, remarks=None):
    recipients = []
    branch = data.get("branch")
    class_data = data.get("class")

    team_lead_id = get_team_lead_id(lead)
    if "team_lead" in sender_keys and team_lead_id:
        recipients.append(team_lead_id)

    if "assigned_to" in sender_keys and lead.assigned_to:
        recipients.append(lead.assigned_to)

    parent_first_name, parent_last_name, parent_email, parent_contact_number = get_lead_parent(lead)
    if "parent_email" in sender_keys and parent_email:
        recipients.append(parent_email)

    last_follow_up_activity = None
    if "last_activity" in sender_keys:
        last_follow_up_activity = get_last_follow_up_activity(lead)

    email_notifications.append(notification_obj(
        trigger,
        recipients,
        {
            'business_id': lead.business_id,
            'business_name': 'Janson co',
            'branch_id': lead.branch_id,
            'branch_name': branch["name"] if branch else None,
            'branch_contact_number': branch["phone"] if branch else None,
            'branch_address': branch["address"] if branch else None,
            'class_name': class_data["name"] if class_data else None,
            'student_name': lead.first_name + " " + lead.last_name,
            'parent_name': parent_first_name + " " + parent_last_name if parent_first_name else None,
            'parent_email': parent_email,
            'parent_contact_number': parent_contact_number,
            'last_activity': DateTimeConverter.from_utc_datetime(last_follow_up_activity['date_time'].isoformat(), user_timezone) if last_follow_up_activity else None,
            'reason_type': stage_reason.name if stage_reason else None,
            'reason': remarks,
            'object_id': lead.stage_id,
            'sub_object_id': stage_reason.id if stage_reason else None,
        }
    ))
        
    return email_notifications
        

def get_last_follow_up_activity(lead):
    last_follow_up = lead.follow_ups.order_by('-created_at').first()
    if last_follow_up:
        return {
            'date_time': last_follow_up.date_time,
        }
    return None

def get_lead_parent(lead):
    lead_contact = lead.contact
    if lead_contact:
        if lead_contact.is_father_applicable:
            return lead_contact.father_first_name, lead_contact.father_last_name, lead_contact.father_email, lead_contact.father_contact_number
        elif lead_contact.is_mother_applicable:
            return lead_contact.mother_first_name, lead_contact.mother_last_name, lead_contact.mother_email, lead_contact.mother_contact_number
    return None, None, None, None

def get_team_lead_id(lead):
    if lead.team and lead.team.user_id:
        return lead.team.user_id
    return None