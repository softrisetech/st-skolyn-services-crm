from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
import uuid
from datetime import datetime, date
from decimal import Decimal
import traceback
from core.audit_models import ActivityLog
def get_current_context():
    """Get current request context from thread local"""
    from core.middleware import _thread_locals
    return _thread_locals


def serialize_value(value):
    """Convert non-JSON-serializable types to strings"""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, uuid.UUID):
        return str(value)
    elif isinstance(value, Decimal):
        return float(value)
    elif hasattr(value, 'pk'):  # ForeignKey
        return str(value.pk)
    elif value is None:
        return None
    elif isinstance(value, (str, int, float, bool)):
        return value
    else:
        return str(value)


def serialize_dict(data):
    """Convert all values in dictionary to JSON-serializable types"""
    if not data:
        return data
    
    serialized = {}
    for key, value in data.items():
        serialized[key] = serialize_value(value)
    return serialized


def get_changed_fields(old_dict, new_dict):
    """Compare two dictionaries and return changed fields"""
    if not old_dict or not new_dict:
        return None
    
    changes = {}
    for key in new_dict:
        if key in old_dict and old_dict[key] != new_dict[key]:
            changes[key] = {
                'old': serialize_value(old_dict[key]),
                'new': serialize_value(new_dict[key])
            }
    return changes if changes else None


def is_soft_delete(old_dict, new_dict):
    """
    Check if this is a soft delete (deleted_at changed from None to a timestamp)
    """
    if not old_dict or not new_dict:
        return False
    
    # Check if deleted_at field exists and changed from None to a value
    if 'deleted_at' in old_dict and 'deleted_at' in new_dict:
        if old_dict['deleted_at'] is None and new_dict['deleted_at'] is not None:
            return True
    
    return False


# Store pre-save state
_pre_save_instances = {}


@receiver(pre_save)
def store_pre_save_instance(sender, instance, **kwargs):
    """Store the state before save for UPDATE comparison"""
    # Skip non-tracked models
    if sender.__name__ in ['ActivityLog', 'ContentType', 'Permission', 'Group', 'Session', 'LogEntry']:
        return
    
    # Only for updates (instance has pk)
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            _pre_save_instances[id(instance)] = model_to_dict(old_instance)
        except sender.DoesNotExist:
            pass


@receiver(post_save)
def log_create_update(sender, instance, created, **kwargs):
    """Log CREATE and UPDATE actions (including soft deletes)"""
    
    # Skip non-tracked models
    if sender.__name__ in ['ActivityLog', 'ContentType', 'Permission', 'Group', 'Session', 'LogEntry']:
        return
    
    # Import ActivityLog
    from core.audit_models import ActivityLog
    
    # Get context from middleware
    context = get_current_context()
    
    # Get auth_id and business_id (can be None)
    business_id = getattr(context, 'business_id', None)
    auth_id = getattr(context, 'auth_id', None)
    
    # Skip ONLY if auth_id is missing
    if not auth_id:
        return
    
    # Determine action
    action = ActivityLog.ACTION_CREATE if created else ActivityLog.ACTION_UPDATE
    
    # Get changes for UPDATE
    changes = None
    if not created:
        old_data = _pre_save_instances.pop(id(instance), None)
        if old_data:
            new_data = model_to_dict(instance)
            
            # Check if this is a soft delete
            if is_soft_delete(old_data, new_data):
                action = ActivityLog.ACTION_DELETE
                # For soft deletes, store the full object data (like hard delete)
                changes = serialize_dict(old_data)
            else:
                # Regular update - just store what changed
                changes = get_changed_fields(old_data, new_data)
    
    # Get content type
    content_type = ContentType.objects.get_for_model(sender)
    
    # Get model name
    model_name = sender.__name__
    
    # Get remote addr
    request = getattr(context, 'request', None)
    remote_addr = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            remote_addr = x_forwarded_for.split(',')[0]
        else:
            remote_addr = request.META.get('REMOTE_ADDR')
    
    # Create activity log
    try:
        log = ActivityLog.objects.create(
            content_type=content_type,
            object_id=instance.pk,
            model_name=model_name,
            action=action,
            changes=changes,
            business_id=business_id,
            auth_id=auth_id,
            remote_addr=remote_addr,
        )
    except Exception as e:
        print(f"❌ Error creating {action} log: {e}")
        import traceback
        traceback.print_exc()


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """Log hard DELETE actions (actual database deletion)"""
        
    # Skip non-tracked models
    if sender.__name__ in ['ActivityLog', 'ContentType', 'Permission', 'Group', 'Session', 'LogEntry']:
        return
    
    # Import ActivityLog
    
    # Get context
    context = get_current_context()
    
    business_id = getattr(context, 'business_id', None)
    auth_id = getattr(context, 'auth_id', None)
    
    
    # Skip if no auth_id
    if not auth_id:
        return
    
    # Get content type
    content_type = ContentType.objects.get_for_model(sender)
    
    # Get model name
    model_name = sender.__name__
    
    # Get remote addr
    request = getattr(context, 'request', None)
    remote_addr = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            remote_addr = x_forwarded_for.split(',')[0]
        else:
            remote_addr = request.META.get('REMOTE_ADDR')
    
    # Store deleted object data
    try:
        old_data = model_to_dict(instance)
        # Serialize to make it JSON-compatible
        old_data = serialize_dict(old_data)
    except Exception as e:
        old_data = {"error": str(e)}
    
    # Create activity log
    try:
        log = ActivityLog.objects.create(
            content_type=content_type,
            object_id=instance.pk,
            model_name=model_name,
            action=ActivityLog.ACTION_DELETE,
            changes=old_data,
            business_id=business_id,
            auth_id=auth_id,
            remote_addr=remote_addr,
        )
    except Exception as e:        
        traceback.print_exc()
        