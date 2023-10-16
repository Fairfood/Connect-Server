"""Celery function to send sms."""
import boto3
from celery import current_app as app
from django.conf import settings
from sentry_sdk import capture_exception


@app.task(name="send_sms", queue="high")
def send_sms(phone_number: str, message: str):
    """Function to send SMS."""
    if not phone_number:
        return False

    from v1.notifications.models import SMSAlerts

    sms = SMSAlerts.objects.create(phone=phone_number, message=message)
    try:
        session = boto3.session.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION,
        )
        sns = session.client("sns")

        # publish the message to the phone number
        response = sns.publish(PhoneNumber=phone_number, Message=message)
        sms.response = response
        sms.save()
        return response["MessageId"]
    except Exception as e:
        capture_exception(e)
        sms.response_text = str(e)
        sms.save()
        return None
