# utils.py
import random
from twilio.rest import Client
from django.conf import settings

def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp_via_twilio(mobile_number, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message_body = f"Your OTP for login is {otp}"
    
    message = client.messages.create(
        body=message_body,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=f"+91{mobile_number}"  # assuming Indian numbers
    )
    return message.sid  # Can be logged for reference
