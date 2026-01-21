def notification(email= '', web = '', sms= '', push= ''):
    notification = {
        'email': email,
        'web': web,
        'sms': sms,
        'push': push
    }
    return notification

def notification_obj(template, recipient_list, attributes={}):
    obj = {
        'template': template,
        'recipient_list': recipient_list,
        'attributes': attributes
    }
    return obj