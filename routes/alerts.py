from flask import Blueprint, request, jsonify
from services.firebase_service import (
    create_sos_alert,
    get_active_alerts,
    resolve_sos_alert,
    start_checkin,
    respond_to_checkin,
    get_checkin_status,
    escalate_checkin,
    stop_checkin,
    get_emergency_contacts,
    save_traveler_location
)
from services.notification import (
    send_sos_sms,
    send_checkin_missed_sms
)

alerts_bp = Blueprint('alerts', __name__)


# ─────────────────────────────────────────
#  SOS ALERTS
# ─────────────────────────────────────────

@alerts_bp.route('/sos', methods=['POST'])
def trigger_sos():
    """
    Trigger an SOS alert manually or via voice code.
    Notifies all emergency contacts via SMS.
    """
    data = request.get_json()
    uid = data.get("uid")

    if not uid:
        return jsonify({"error": "uid is required"}), 400

    required = ['latitude', 'longitude']
    for field in required:
        if data.get(field) is None:
            return jsonify({"error": f"'{field}' is required"}), 400

    # Create SOS alert in Firestore
    alert = create_sos_alert(uid, {
        "type": data.get("type", "manual"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "message": data.get("message", "SOS! I need help!")
    })

    # Notify emergency contacts via SMS
    contacts = get_emergency_contacts(uid)
    maps_link = f"https://maps.google.com/?q={data.get('latitude')},{data.get('longitude')}"
    message = f"🆘 SOS ALERT! Your contact needs help!\nLocation: {maps_link}\nMessage: {alert['message']}"

    for contact in contacts:
        if contact.get("phone"):
            send_sos_sms(contact["phone"], message)

    return jsonify({
        "message": "SOS alert triggered successfully",
        "alert": alert,
        "contacts_notified": len(contacts)
    }), 201


@alerts_bp.route('/sos/<uid>', methods=['GET'])
def get_alerts(uid):
    """Get all active SOS alerts for a user"""
    alerts = get_active_alerts(uid)
    return jsonify({"alerts": alerts}), 200


@alerts_bp.route('/sos/<alert_id>/resolve', methods=['PUT'])
def resolve_alert(alert_id):
    """Resolve/dismiss an active SOS alert"""
    resolve_sos_alert(alert_id)
    return jsonify({"message": "Alert resolved successfully"}), 200


# ─────────────────────────────────────────
#  DEAD MAN'S SWITCH (CHECK-IN)
# ─────────────────────────────────────────

@alerts_bp.route('/checkin/start', methods=['POST'])
def start_dead_mans_switch():
    """
    Start the Dead Man's Switch.
    Frontend should ping /checkin/check every N minutes.
    If no response received → escalate.
    """
    data = request.get_json()
    uid = data.get("uid")
    interval = data.get("interval_minutes", 30)

    if not uid:
        return jsonify({"error": "uid is required"}), 400

    if not isinstance(interval, int) or interval < 1:
        return jsonify({"error": "interval_minutes must be a positive integer"}), 400

    checkin = start_checkin(uid, interval)
    return jsonify({
        "message": f"Dead Man's Switch started. Check-in every {interval} minutes.",
        "checkin": checkin
    }), 201


@alerts_bp.route('/checkin/respond', methods=['POST'])
def respond_checkin():
    """User responds 'I'm okay' to a check-in prompt"""
    data = request.get_json()
    uid = data.get("uid")

    if not uid:
        return jsonify({"error": "uid is required"}), 400

    respond_to_checkin(uid)
    return jsonify({"message": "Check-in response recorded. You're safe!"}), 200


@alerts_bp.route('/checkin/status/<uid>', methods=['GET'])
def checkin_status(uid):
    """Get the current Dead Man's Switch status"""
    status = get_checkin_status(uid)
    if not status:
        return jsonify({"error": "No active check-in session found"}), 404
    return jsonify(status), 200


@alerts_bp.route('/checkin/escalate', methods=['POST'])
def escalate():
    """
    Called when user does NOT respond to check-in in time.
    Marks as escalated and notifies emergency contacts via SMS.
    """
    data = request.get_json()
    uid = data.get("uid")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not uid:
        return jsonify({"error": "uid is required"}), 400

    escalate_checkin(uid)

    # Notify emergency contacts
    contacts = get_emergency_contacts(uid)
    maps_link = f"https://maps.google.com/?q={latitude},{longitude}" if latitude and longitude else "Location unavailable"
    message = f"⚠️ NO RESPONSE ALERT! Your contact has not responded to their safety check-in.\nLast known location: {maps_link}"

    for contact in contacts:
        if contact.get("phone"):
            send_checkin_missed_sms(contact["phone"], message)

    return jsonify({
        "message": "Escalation triggered. Emergency contacts notified.",
        "contacts_notified": len(contacts)
    }), 200


@alerts_bp.route('/checkin/stop', methods=['POST'])
def stop_dead_mans_switch():
    """Stop the Dead Man's Switch"""
    data = request.get_json()
    uid = data.get("uid")

    if not uid:
        return jsonify({"error": "uid is required"}), 400

    stop_checkin(uid)
    return jsonify({"message": "Dead Man's Switch stopped successfully"}), 200


# ─────────────────────────────────────────
#  TRAVELER SAFETY MODE
# ─────────────────────────────────────────

# Local emergency numbers by country code
EMERGENCY_DATA = {
    "IN": {
        "country": "India",
        "police": "100", "ambulance": "108", "fire": "101",
        "women_helpline": "1091",
        "emergency_phrase": "Madad karo! Mujhe madad chahiye!",
        "embassy_search": "https://www.indianembassy.org"
    },
    "US": {
        "country": "United States",
        "police": "911", "ambulance": "911", "fire": "911",
        "emergency_phrase": "Help! I need assistance!",
        "embassy_search": "https://www.usembassy.gov"
    },
    "GB": {
        "country": "United Kingdom",
        "police": "999", "ambulance": "999", "fire": "999",
        "emergency_phrase": "Help! Call the police!",
        "embassy_search": "https://www.gov.uk/world/embassies"
    },
    "AU": {
        "country": "Australia",
        "police": "000", "ambulance": "000", "fire": "000",
        "emergency_phrase": "Help! I need emergency assistance!",
        "embassy_search": "https://protocol.dfat.gov.au"
    },
    "DE": {
        "country": "Germany",
        "police": "110", "ambulance": "112", "fire": "112",
        "emergency_phrase": "Hilfe! Ich brauche Hilfe!",
        "embassy_search": "https://www.auswaertiges-amt.de"
    },
    "FR": {
        "country": "France",
        "police": "17", "ambulance": "15", "fire": "18",
        "emergency_phrase": "Au secours! J'ai besoin d'aide!",
        "embassy_search": "https://www.diplomatie.gouv.fr"
    },
}


@alerts_bp.route('/traveler/info', methods=['POST'])
def traveler_info():
    """
    Given a country code from the frontend (detected via GPS),
    return local emergency numbers, embassy info, and emergency phrases.
    """
    data = request.get_json()
    uid = data.get("uid")
    country_code = data.get("country_code", "").upper()
    country_name = data.get("country_name", "")

    if not uid or not country_code:
        return jsonify({"error": "uid and country_code are required"}), 400

    # Save to Firestore (non critical)
    try:
       save_traveler_location(uid, country_code, country_name)
    except Exception as e:
       print(f"[WARNING] Could not save traveler location: {str(e)}")

    emergency_info = EMERGENCY_DATA.get(country_code, {
        "country": country_name or country_code,
        "police": "112",
        "ambulance": "112",
        "fire": "112",
        "emergency_phrase": "Help! I need assistance!",
        "embassy_search": f"https://www.google.com/search?q={country_name}+emergency+numbers"
    })

    return jsonify({
        "message": "Traveler Safety Mode activated",
        "country_code": country_code,
        "emergency_info": emergency_info
    }), 200


# ─────────────────────────────────────────
#  FIRST AID HELP
# ─────────────────────────────────────────

FIRST_AID_DATA = {
    "cpr": {
        "title": "CPR (Cardiopulmonary Resuscitation)",
        "steps": [
            "Call emergency services (112/911) immediately.",
            "Place the person on their back on a firm surface.",
            "Tilt head back slightly and lift the chin to open airway.",
            "Give 30 chest compressions — hard and fast in the center of the chest.",
            "Give 2 rescue breaths — pinch nose, cover mouth, breathe in.",
            "Repeat 30:2 cycle until help arrives or person recovers."
        ]
    },
    "bleeding": {
        "title": "Severe Bleeding",
        "steps": [
            "Apply firm pressure with a clean cloth or bandage.",
            "Do not remove the cloth — add more on top if it soaks through.",
            "Elevate the injured area above heart level if possible.",
            "Keep applying pressure for at least 10–15 minutes.",
            "Call emergency services immediately."
        ]
    },
    "choking": {
        "title": "Choking",
        "steps": [
            "Ask 'Are you choking?' — if they cannot speak, act immediately.",
            "Give 5 back blows between shoulder blades with heel of hand.",
            "Give 5 abdominal thrusts (Heimlich maneuver).",
            "Alternate back blows and abdominal thrusts.",
            "If person becomes unconscious, begin CPR and call emergency services."
        ]
    },
    "burn": {
        "title": "Burns",
        "steps": [
            "Cool the burn under cool (not cold) running water for 10–20 minutes.",
            "Do NOT use ice, butter, or creams.",
            "Remove jewelry/clothing near the burn (unless stuck).",
            "Cover loosely with a clean non-fluffy material.",
            "Seek medical help for burns larger than a palm size."
        ]
    },
    "fracture": {
        "title": "Fracture / Broken Bone",
        "steps": [
            "Do not try to straighten the bone.",
            "Immobilize the injured area using a splint or padding.",
            "Apply ice wrapped in cloth to reduce swelling.",
            "Keep the person still and calm.",
            "Call emergency services immediately."
        ]
    },
    "seizure": {
        "title": "Seizure",
        "steps": [
            "Stay calm and stay with the person.",
            "Clear away dangerous objects nearby.",
            "Do NOT hold the person down or put anything in their mouth.",
            "Gently cushion their head.",
            "After seizure ends, turn them on their side (recovery position).",
            "Call emergency services if seizure lasts more than 5 minutes."
        ]
    }
}


@alerts_bp.route('/firstaid', methods=['POST'])
def first_aid():
    """
    Accept a first aid keyword and return step-by-step instructions.
    Keywords: cpr, bleeding, choking, burn, fracture, seizure
    """
    data = request.get_json()
    keyword = data.get("keyword", "").lower().strip()

    if not keyword:
        return jsonify({"error": "keyword is required"}), 400

    # Try exact match first
    instructions = FIRST_AID_DATA.get(keyword)

    # Try partial match if no exact match
    if not instructions:
        for key in FIRST_AID_DATA:
            if keyword in key or key in keyword:
                instructions = FIRST_AID_DATA[key]
                break

    if not instructions:
        return jsonify({
            "error": "No instructions found for this keyword",
            "available_keywords": list(FIRST_AID_DATA.keys())
        }), 404

    return jsonify({
        "keyword": keyword,
        "instructions": instructions
    }), 200


@alerts_bp.route('/firstaid/keywords', methods=['GET'])
def get_firstaid_keywords():
    """Get all available first aid keywords"""
    keywords = [{"keyword": k, "title": v["title"]} for k, v in FIRST_AID_DATA.items()]
    return jsonify({"keywords": keywords}), 200