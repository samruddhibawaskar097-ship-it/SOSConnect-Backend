from flask import Blueprint, request, jsonify
from services.firebase_service import create_user, get_user
import random
import time

auth_bp = Blueprint('auth', __name__)

# Temporary OTP storage (in production use Redis or Firebase)
otp_store = {}


# ─────────────────────────────────────────
#  SEND OTP
# ─────────────────────────────────────────

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Generate and send OTP to phone number"""
    data = request.get_json()
    phone = data.get("phone")
    name = data.get("name")

    if not phone:
        return jsonify({"error": "Phone number is required"}), 400

    # Format phone number
    if not phone.startswith("+"):
        phone = "+91" + phone

    # Generate 6 digit OTP
    otp = str(random.randint(100000, 999999))

    # Store OTP with timestamp (expires in 5 minutes)
    otp_store[phone] = {
        "otp": otp,
        "name": name,
        "timestamp": time.time()
    }

    # In production: send via Twilio SMS
    # For now: return OTP in response (for testing)
    try:
        from services.notification import send_sms
        send_sms(phone, f"Your SOSConnect OTP is: {otp}. Valid for 5 minutes.")
        print(f"[OTP] Sent to {phone}: {otp}")
    except Exception as e:
        print(f"[OTP] SMS failed: {str(e)}, OTP: {otp}")

    return jsonify({
        "message": "OTP sent successfully",
        "phone": phone,
        # Remove otp from response in production!
        "otp_debug": otp  # ← Remove this in production
    }), 200


# ─────────────────────────────────────────
#  VERIFY OTP
# ─────────────────────────────────────────

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and register/login user"""
    data = request.get_json()
    phone = data.get("phone")
    otp = data.get("otp")
    name = data.get("name", "User")

    if not phone or not otp:
        return jsonify({"error": "Phone and OTP are required"}), 400

    # Format phone
    if not phone.startswith("+"):
        phone = "+91" + phone

    # Check OTP exists
    if phone not in otp_store:
        return jsonify({"error": "OTP not found. Please request a new one."}), 400

    stored = otp_store[phone]

    # Check expiry (5 minutes)
    if time.time() - stored["timestamp"] > 300:
        del otp_store[phone]
        return jsonify({"error": "OTP expired. Please request a new one."}), 400

    # Verify OTP
    if stored["otp"] != otp:
        return jsonify({"error": "Invalid OTP. Please try again."}), 400

    # OTP correct - clear it
    del otp_store[phone]

    # Generate UID from phone
    uid = "user_" + phone.replace("+", "").replace(" ", "")
    email = uid + "@sosconnect.app"
    user_name = stored.get("name") or name

    # Register user in Firebase (if not exists)
    try:
        existing = get_user(uid)
        if not existing:
            create_user(uid, {
                "uid": uid,
                "name": user_name,
                "phone": phone,
                "email": email,
                "emergency_contacts": [],
                "distress_phrase": None
            })
    except Exception as e:
        print(f"[AUTH] User creation note: {str(e)}")

    return jsonify({
        "message": "Login successful",
        "uid": uid,
        "name": user_name,
        "phone": phone,
        "email": email
    }), 200


# ─────────────────────────────────────────
#  CHECK USER EXISTS
# ─────────────────────────────────────────

@auth_bp.route('/check-user/<phone>', methods=['GET'])
def check_user(phone):
    """Check if user exists by phone number"""
    if not phone.startswith("+"):
        phone = "+91" + phone

    uid = "user_" + phone.replace("+", "").replace(" ", "")

    try:
        user = get_user(uid)
        if user:
            return jsonify({"exists": True, "uid": uid}), 200
        else:
            return jsonify({"exists": False}), 200
    except Exception as e:
        return jsonify({"exists": False}), 200
