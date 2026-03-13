from config.firebase_config import db
from datetime import datetime


# ─────────────────────────────────────────
#  USER SERVICES
# ─────────────────────────────────────────

def create_user(uid, data):
    """Create a new user profile in Firestore"""
    user_data = {
        "uid": uid,
        "name": data.get("name"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "emergency_contacts": [],
        "distress_phrase": None,
        "created_at": datetime.utcnow().isoformat()
    }
    db.collection("users").document(uid).set(user_data)
    return user_data


def get_user(uid):
    """Get a user profile by UID"""
    doc = db.collection("users").document(uid).get()
    return doc.to_dict() if doc.exists else None


def update_user(uid, data):
    """Update user profile fields"""
    db.collection("users").document(uid).update(data)
    return True


# ─────────────────────────────────────────
#  EMERGENCY CONTACTS SERVICES
# ─────────────────────────────────────────

def add_emergency_contact(uid, contact):
    """Add an emergency contact to a user's profile"""
    user_ref = db.collection("users").document(uid)
    user = user_ref.get().to_dict()
    contacts = user.get("emergency_contacts", [])
    contacts.append({
        "name": contact.get("name"),
        "phone": contact.get("phone"),
        "email": contact.get("email"),
        "added_at": datetime.utcnow().isoformat()
    })
    user_ref.update({"emergency_contacts": contacts})
    return contacts


def get_emergency_contacts(uid):
    """Get all emergency contacts of a user"""
    user = get_user(uid)
    return user.get("emergency_contacts", []) if user else []


def remove_emergency_contact(uid, phone):
    """Remove an emergency contact by phone number"""
    user_ref = db.collection("users").document(uid)
    user = user_ref.get().to_dict()
    contacts = user.get("emergency_contacts", [])
    updated = [c for c in contacts if c.get("phone") != phone]
    user_ref.update({"emergency_contacts": updated})
    return updated


# ─────────────────────────────────────────
#  SOS ALERT SERVICES
# ─────────────────────────────────────────

def create_sos_alert(uid, data):
    """Create a new SOS alert"""
    alert_data = {
        "uid": uid,
        "type": data.get("type", "manual"),   # manual | voice | checkin | traveler
        "status": "active",
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "message": data.get("message", "SOS! I need help!"),
        "triggered_at": datetime.utcnow().isoformat(),
        "resolved_at": None
    }
    ref = db.collection("sos_alerts").document()
    ref.set(alert_data)
    alert_data["alert_id"] = ref.id
    return alert_data


def get_active_alerts(uid):
    """Get all active SOS alerts for a user"""
    alerts = db.collection("sos_alerts")\
        .where("uid", "==", uid)\
        .where("status", "==", "active")\
        .stream()
    return [{"alert_id": a.id, **a.to_dict()} for a in alerts]


def resolve_sos_alert(alert_id):
    """Mark a SOS alert as resolved"""
    db.collection("sos_alerts").document(alert_id).update({
        "status": "resolved",
        "resolved_at": datetime.utcnow().isoformat()
    })
    return True


# ─────────────────────────────────────────
#  DEAD MAN'S SWITCH (CHECK-IN) SERVICES
# ─────────────────────────────────────────

def start_checkin(uid, interval_minutes):
    """Start a dead man's switch check-in session"""
    checkin_data = {
        "uid": uid,
        "interval_minutes": interval_minutes,
        "status": "active",
        "last_response": datetime.utcnow().isoformat(),
        "started_at": datetime.utcnow().isoformat(),
        "escalated": False
    }
    ref = db.collection("checkins").document(uid)
    ref.set(checkin_data)
    return checkin_data


def respond_to_checkin(uid):
    """User responds 'I'm okay' to a check-in"""
    db.collection("checkins").document(uid).update({
        "last_response": datetime.utcnow().isoformat(),
        "escalated": False
    })
    return True


def get_checkin_status(uid):
    """Get current check-in session status"""
    doc = db.collection("checkins").document(uid).get()
    return doc.to_dict() if doc.exists else None


def escalate_checkin(uid):
    """Mark check-in as escalated (no response received)"""
    db.collection("checkins").document(uid).update({
        "escalated": True,
        "escalated_at": datetime.utcnow().isoformat()
    })
    return True


def stop_checkin(uid):
    """Stop the dead man's switch"""
    db.collection("checkins").document(uid).update({
        "status": "stopped",
        "stopped_at": datetime.utcnow().isoformat()
    })
    return True


# ─────────────────────────────────────────
#  SILENT VOICE CODE SERVICES
# ─────────────────────────────────────────

def save_distress_phrase(uid, phrase):
    """Save a user's secret distress phrase"""
    db.collection("users").document(uid).update({
        "distress_phrase": phrase.lower().strip()
    })
    return True


def get_distress_phrase(uid):
    """Get a user's distress phrase"""
    user = get_user(uid)
    return user.get("distress_phrase") if user else None


# ─────────────────────────────────────────
#  TRAVELER SAFETY MODE SERVICES
# ─────────────────────────────────────────

def save_traveler_location(uid, country_code, country_name):
    """Save user's detected travel location"""
    db.collection("users").document(uid).update({
        "traveler_mode": {
            "active": True,
            "country_code": country_code,
            "country_name": country_name,
            "detected_at": datetime.utcnow().isoformat()
        }
    })
    return True