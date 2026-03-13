import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv

# Explicitly point to the .env file in backend/
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

def send_sms(to_phone, message):
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        messaging_sid = os.getenv("TWILIO_MESSAGING_SERVICE_SID")
        client = Client(account_sid, auth_token)
        client.messages.create(
            body=message,
            messaging_service_sid=messaging_sid,
            to=to_phone
        )
        print(f"[SMS SENT] To: {to_phone}")
        return True
    except Exception as e:
        print(f"[SMS FAILED] To: {to_phone} | Error: {str(e)}")
        return False

def send_sos_sms(to_phone, message):
    return send_sms(to_phone, message)

def send_checkin_missed_sms(to_phone, message):
    return send_sms(to_phone, message)

def make_call(to_phone, message):
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_phone = os.getenv("TWILIO_PHONE_NUMBER")
        client = Client(account_sid, auth_token)
        response = VoiceResponse()
        response.say(message, voice='alice', language='en-IN')
        response.pause(length=1)
        response.say(message, voice='alice', language='en-IN')
        client.calls.create(
            twiml=str(response),
            from_=from_phone,
            to=to_phone
        )
        print(f"[CALL MADE] To: {to_phone}")
        return True
    except Exception as e:
        print(f"[CALL FAILED] To: {to_phone} | Error: {str(e)}")
        return False

def make_sos_call(to_phone, user_name, location_link):
    message = (
        f"Emergency alert from SOS Connect! "
        f"{user_name} needs immediate help! "
        f"Please check your SMS for their location. "
        f"Contact them or emergency services immediately!"
    )
    return make_call(to_phone, message)

def notify_contact(contact, user_name, sms_message, call=True):
    phone = contact.get("phone")
    if not phone:
        return False
    sms_sent = send_sms(phone, sms_message)
    call_made = False
    if call:
        call_made = make_sos_call(phone, user_name, sms_message)
    return {
        "phone": phone,
        "sms_sent": sms_sent,
        "call_made": call_made
    }

    