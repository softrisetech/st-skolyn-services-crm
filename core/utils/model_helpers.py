from leads.models import Stage, Tracking

def opportunity_default_stage_exists(business_id):
    flag = False
    default_stage = opportunity_default_stage(business_id)
    if default_stage:
        flag = True
    return flag

def opportunity_default_stage(business_id):
    default_stage_id = None
    default_stage = Stage.objects.filter(
        business_id=business_id,
        is_default=True,
    ).first()

    # If no default stage found, get first stage sorted by priority
    if not default_stage:
        default_stage = Stage.objects.filter(
            business_id=business_id,
            status="open"
        ).order_by('priority').first()

    if default_stage:
        default_stage_id = default_stage.id

    return default_stage_id

def lead_default_stage(business_id):
    default_stage_id = None
    default_stage = Stage.objects.filter(
        business_id=business_id,
        is_default=True,
    ).first()

    # If no default stage found, get first stage sorted by priority
    if not default_stage:
        default_stage = Stage.objects.filter(
            business_id=business_id,
            status="open"
        ).order_by('priority').first()

    if default_stage:
        default_stage_id = default_stage.id

    return default_stage_id

def tracking_object(business_id, lead_id, model_id, model_type, user_id):
    return Tracking(
                business_id=business_id,
                lead_id=lead_id,
                model_id=model_id,
                model_type=model_type,
                user_id=user_id
            )

def verify_lead_missing_fields(record):
    missing_fields = []
    if not record.name:
        missing_fields.append("Name")

    if not record.contact_number:
        missing_fields.append("Contact no")

    if not record.branch_id:
        missing_fields.append("Branch")

    if not record.session_id:
        missing_fields.append("Session")

    if not record.medium_id:
        missing_fields.append("Medium")

    if not record.source_id:
        missing_fields.append("Source")

    if not record.p_contact_number:
        missing_fields.append("Parent contact number")

    return missing_fields

