from flask import Blueprint, request, jsonify
from services.navigation_service import (
    get_nearby_hospitals,
    get_nearby_police,
    get_nearby_pharmacies,
    get_directions
)
from services.firebase_service import update_user

navigation_bp = Blueprint('navigation', __name__)


# ─────────────────────────────────────────
#  SAVE USER LIVE LOCATION
# ─────────────────────────────────────────

@navigation_bp.route('/location', methods=['POST'])
def save_location():
    """Save user's current live location to Firebase"""
    data = request.get_json()
    uid = data.get("uid")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not uid or latitude is None or longitude is None:
        return jsonify({"error": "uid, latitude and longitude are required"}), 400

    update_user(uid, {
        "live_location": {
            "latitude": latitude,
            "longitude": longitude,
            "updated_at": __import__('datetime').datetime.utcnow().isoformat()
        }
    })

    return jsonify({
        "message": "Location updated successfully",
        "latitude": latitude,
        "longitude": longitude,
        "google_maps_link": f"https://maps.google.com/?q={latitude},{longitude}"
    }), 200


# ─────────────────────────────────────────
#  NEARBY HOSPITALS
# ─────────────────────────────────────────

@navigation_bp.route('/nearby/hospitals', methods=['POST'])
def nearby_hospitals():
    """Find nearby hospitals"""
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    radius = data.get("radius", 5000)

    if latitude is None or longitude is None:
        return jsonify({"error": "latitude and longitude are required"}), 400

    hospitals = get_nearby_hospitals(latitude, longitude, radius)

    return jsonify({
        "type": "hospitals",
        "count": len(hospitals),
        "results": hospitals
    }), 200


# ─────────────────────────────────────────
#  NEARBY POLICE STATIONS
# ─────────────────────────────────────────

@navigation_bp.route('/nearby/police', methods=['POST'])
def nearby_police():
    """Find nearby police stations"""
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    radius = data.get("radius", 5000)

    if latitude is None or longitude is None:
        return jsonify({"error": "latitude and longitude are required"}), 400

    police = get_nearby_police(latitude, longitude, radius)

    return jsonify({
        "type": "police_stations",
        "count": len(police),
        "results": police
    }), 200


# ─────────────────────────────────────────
#  NEARBY PHARMACIES
# ─────────────────────────────────────────

@navigation_bp.route('/nearby/pharmacies', methods=['POST'])
def nearby_pharmacies():
    """Find nearby pharmacies"""
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    radius = data.get("radius", 3000)

    if latitude is None or longitude is None:
        return jsonify({"error": "latitude and longitude are required"}), 400

    pharmacies = get_nearby_pharmacies(latitude, longitude, radius)

    return jsonify({
        "type": "pharmacies",
        "count": len(pharmacies),
        "results": pharmacies
    }), 200


# ─────────────────────────────────────────
#  GET DIRECTIONS
# ─────────────────────────────────────────

@navigation_bp.route('/directions', methods=['POST'])
def directions():
    """
    Get directions from user's location to a destination.
    mode: driving | walking | transit
    """
    data = request.get_json()
    origin_lat = data.get("origin_lat")
    origin_lng = data.get("origin_lng")
    dest_lat = data.get("dest_lat")
    dest_lng = data.get("dest_lng")
    mode = data.get("mode", "driving")

    if None in [origin_lat, origin_lng, dest_lat, dest_lng]:
        return jsonify({"error": "origin_lat, origin_lng, dest_lat, dest_lng are required"}), 400

    if mode not in ["driving", "walking", "transit"]:
        return jsonify({"error": "mode must be driving, walking, or transit"}), 400

    result = get_directions(origin_lat, origin_lng, dest_lat, dest_lng, mode)

    if not result:
        return jsonify({"error": "Could not get directions. Please try again."}), 500

    return jsonify(result), 200


# ─────────────────────────────────────────
#  ALL NEARBY EMERGENCY PLACES AT ONCE
# ─────────────────────────────────────────

@navigation_bp.route('/nearby/all', methods=['POST'])
def nearby_all():
    """Get all nearby emergency places in one call"""
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({"error": "latitude and longitude are required"}), 400

    hospitals = get_nearby_hospitals(latitude, longitude)
    police = get_nearby_police(latitude, longitude)
    pharmacies = get_nearby_pharmacies(latitude, longitude)

    return jsonify({
        "hospitals": hospitals,
        "police_stations": police,
        "pharmacies": pharmacies,
        "google_maps_link": f"https://maps.google.com/?q={latitude},{longitude}"
    }), 200
from flask import Blueprint, request, jsonify
from services.navigation_service import (
    get_nearby_hospitals,
    get_nearby_police,
    get_nearby_pharmacies,
    get_directions
)
from services.firebase_service import update_user

navigation_bp = Blueprint('navigation', __name__)


# ─────────────────────────────────────────
#  SAVE USER LIVE LOCATION
# ─────────────────────────────────────────

@navigation_bp.route('/location', methods=['POST'])
def save_location():
    """Save user's current live location to Firebase"""
    data = request.get_json()
    uid = data.get("uid")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not uid or latitude is None or longitude is None:
        return jsonify({"error": "uid, latitude and longitude are required"}), 400

    update_user(uid, {
        "live_location": {
            "latitude": latitude,
            "longitude": longitude,
            "updated_at": __import__('datetime').datetime.utcnow().isoformat()
        }
    })

    return jsonify({
        "message": "Location updated successfully",
        "latitude": latitude,
        "longitude": longitude,
        "google_maps_link": f"https://maps.google.com/?q={latitude},{longitude}"
    }), 200


# ─────────────────────────────────────────
#  NEARBY HOSPITALS
# ─────────────────────────────────────────

@navigation_bp.route('/nearby/hospitals', methods=['POST'])
def nearby_hospitals():
    """Find nearby hospitals"""
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    radius = data.get("radius", 5000)

    if latitude is None or longitude is None:
        return jsonify({"error": "latitude and longitude are required"}), 400

    hospitals = get_nearby_hospitals(latitude, longitude, radius)

    return jsonify({
        "type": "hospitals",
        "count": len(hospitals),
        "results": hospitals
    }), 200


# ─────────────────────────────────────────
#  NEARBY POLICE STATIONS
# ─────────────────────────────────────────

@navigation_bp.route('/nearby/police', methods=['POST'])
def nearby_police():
    """Find nearby police stations"""
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    radius = data.get("radius", 5000)

    if latitude is None or longitude is None:
        return jsonify({"error": "latitude and longitude are required"}), 400

    police = get_nearby_police(latitude, longitude, radius)

    return jsonify({
        "type": "police_stations",
        "count": len(police),
        "results": police
    }), 200


# ─────────────────────────────────────────
#  NEARBY PHARMACIES
# ─────────────────────────────────────────

@navigation_bp.route('/nearby/pharmacies', methods=['POST'])
def nearby_pharmacies():
    """Find nearby pharmacies"""
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    radius = data.get("radius", 3000)

    if latitude is None or longitude is None:
        return jsonify({"error": "latitude and longitude are required"}), 400

    pharmacies = get_nearby_pharmacies(latitude, longitude, radius)

    return jsonify({
        "type": "pharmacies",
        "count": len(pharmacies),
        "results": pharmacies
    }), 200


# ─────────────────────────────────────────
#  GET DIRECTIONS
# ─────────────────────────────────────────

@navigation_bp.route('/directions', methods=['POST'])
def directions():
    """
    Get directions from user's location to a destination.
    mode: driving | walking | transit
    """
    data = request.get_json()
    origin_lat = data.get("origin_lat")
    origin_lng = data.get("origin_lng")
    dest_lat = data.get("dest_lat")
    dest_lng = data.get("dest_lng")
    mode = data.get("mode", "driving")

    if None in [origin_lat, origin_lng, dest_lat, dest_lng]:
        return jsonify({"error": "origin_lat, origin_lng, dest_lat, dest_lng are required"}), 400

    if mode not in ["driving", "walking", "transit"]:
        return jsonify({"error": "mode must be driving, walking, or transit"}), 400

    result = get_directions(origin_lat, origin_lng, dest_lat, dest_lng, mode)

    if not result:
        return jsonify({"error": "Could not get directions. Please try again."}), 500

    return jsonify(result), 200


# ─────────────────────────────────────────
#  ALL NEARBY EMERGENCY PLACES AT ONCE
# ─────────────────────────────────────────

@navigation_bp.route('/nearby/all', methods=['POST'])
def nearby_all():
    """Get all nearby emergency places in one call"""
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({"error": "latitude and longitude are required"}), 400

    hospitals = get_nearby_hospitals(latitude, longitude)
    police = get_nearby_police(latitude, longitude)
    pharmacies = get_nearby_pharmacies(latitude, longitude)

    return jsonify({
        "hospitals": hospitals,
        "police_stations": police,
        "pharmacies": pharmacies,
        "google_maps_link": f"https://maps.google.com/?q={latitude},{longitude}"
    }), 200
