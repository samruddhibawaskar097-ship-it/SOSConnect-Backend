from flask import Blueprint, request, jsonify
from services.firebase_service import (
    create_user,
    get_user,
    update_user,
    add_emergency_contact,
    get_emergency_contacts,
    remove_emergency_contact,
    save_distress_phrase,
    get_distress_phrase
)

users_bp = Blueprint('users', __name__)


# ─────────────────────────────────────────
#  USER REGISTRATION & PROFILE
# ─────────────────────────────────────────

@users_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()

    required = ['uid', 'name', 'email', 'phone']
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"'{field}' is required"}), 400

    existing = get_user(data['uid'])
    if existing:
        return jsonify({"error": "User already exists"}), 409

    user = create_user(data['uid'], data)
    return jsonify({"message": "User registered successfully", "user": user}), 201


@users_bp.route('/<uid>', methods=['GET'])
def get_profile(uid):
    """Get user profile"""
    user = get_user(uid)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200


@users_bp.route('/<uid>', methods=['PUT'])
def update_profile(uid):
    """Update user profile"""
    data = request.get_json()

    allowed_fields = ['name', 'phone']
    update_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not update_data:
        return jsonify({"error": "No valid fields to update"}), 400

    update_user(uid, update_data)
    return jsonify({"message": "Profile updated successfully"}), 200


# ─────────────────────────────────────────
#  EMERGENCY CONTACTS
# ─────────────────────────────────────────

@users_bp.route('/<uid>/contacts', methods=['GET'])
def get_contacts(uid):
    """Get all emergency contacts"""
    contacts = get_emergency_contacts(uid)
    return jsonify({"contacts": contacts}), 200


@users_bp.route('/<uid>/contacts', methods=['POST'])
def add_contact(uid):
    """Add an emergency contact"""
    data = request.get_json()

    required = ['name', 'phone']
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"'{field}' is required"}), 400

    contacts = add_emergency_contact(uid, data)
    return jsonify({"message": "Contact added successfully", "contacts": contacts}), 201


@users_bp.route('/<uid>/contacts/<phone>', methods=['DELETE'])
def remove_contact(uid, phone):
    """Remove an emergency contact by phone"""
    updated = remove_emergency_contact(uid, phone)
    return jsonify({"message": "Contact removed", "contacts": updated}), 200


# ─────────────────────────────────────────
#  SILENT SOS VOICE CODE
# ─────────────────────────────────────────

@users_bp.route('/<uid>/distress-phrase', methods=['POST'])
def set_distress_phrase(uid):
    """Save a secret distress phrase"""
    data = request.get_json()
    phrase = data.get("phrase", "").strip()

    if not phrase:
        return jsonify({"error": "Phrase is required"}), 400

    if len(phrase) < 3:
        return jsonify({"error": "Phrase too short, minimum 3 characters"}), 400

    save_distress_phrase(uid, phrase)
    return jsonify({"message": "Distress phrase saved successfully"}), 200


@users_bp.route('/<uid>/distress-phrase/match', methods=['POST'])
def match_distress_phrase(uid):
    """
    Check if a spoken phrase matches the user's distress phrase.
    Frontend sends detected voice text → backend checks if it matches.
    If match → SOS should be triggered by frontend.
    """
    data = request.get_json()
    spoken = data.get("spoken", "").lower().strip()

    if not spoken:
        return jsonify({"error": "Spoken phrase is required"}), 400

    saved_phrase = get_distress_phrase(uid)

    if not saved_phrase:
        return jsonify({"error": "No distress phrase set for this user"}), 404

    matched = saved_phrase in spoken or spoken in saved_phrase

    return jsonify({
        "matched": matched,
        "trigger_sos": matched
    }), 200