import os
import requests
from dotenv import load_dotenv

# Load .env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)


# ─────────────────────────────────────────
#  OPENSTREETMAP - OVERPASS API (FREE)
#  No API key needed!
# ─────────────────────────────────────────

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def query_nearby_places(latitude, longitude, radius, amenity):
    """
    Query OpenStreetMap for nearby places using Overpass API.
    amenity: hospital | police | pharmacy | fire_station
    """
    try:
        query = f"""
        [out:json];
        (
          node["amenity"="{amenity}"](around:{radius},{latitude},{longitude});
          way["amenity"="{amenity}"](around:{radius},{latitude},{longitude});
        );
        out center 5;
        """
        response = requests.post(OVERPASS_URL, data=query, timeout=10)
        data = response.json()
        return _format_osm_places(data.get('elements', []), latitude, longitude)
    except Exception as e:
        print(f"[OSM ERROR] {amenity}: {str(e)}")
        return []


def get_nearby_hospitals(latitude, longitude, radius=5000):
    """Find nearby hospitals"""
    return query_nearby_places(latitude, longitude, radius, 'hospital')


def get_nearby_police(latitude, longitude, radius=5000):
    """Find nearby police stations"""
    return query_nearby_places(latitude, longitude, radius, 'police')


def get_nearby_pharmacies(latitude, longitude, radius=3000):
    """Find nearby pharmacies"""
    return query_nearby_places(latitude, longitude, radius, 'pharmacy')


def get_nearby_fire_stations(latitude, longitude, radius=5000):
    """Find nearby fire stations"""
    return query_nearby_places(latitude, longitude, radius, 'fire_station')


# ─────────────────────────────────────────
#  DIRECTIONS (using OSRM - also free!)
# ─────────────────────────────────────────

def get_directions(origin_lat, origin_lng, dest_lat, dest_lng, mode='driving'):
    """
    Get directions using OSRM (Open Source Routing Machine) - completely free!
    mode: driving | walking
    """
    try:
        profile = 'car' if mode == 'driving' else 'foot'
        url = f"http://router.project-osrm.org/route/v1/{profile}/{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
        params = {
            "overview": "false",
            "steps": "true"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get('code') != 'Ok':
            return None

        route = data['routes'][0]
        leg = route['legs'][0]

        steps = []
        for step in leg.get('steps', []):
            maneuver = step.get('maneuver', {})
            steps.append({
                "instruction": _get_instruction(maneuver),
                "distance": f"{round(step['distance'])} m",
                "duration": f"{round(step['duration'] / 60, 1)} min"
            })

        return {
            "total_distance": f"{round(route['distance'] / 1000, 2)} km",
            "total_duration": f"{round(route['duration'] / 60, 1)} min",
            "mode": mode,
            "steps": steps,
            "google_maps_link": f"https://maps.google.com/maps?saddr={origin_lat},{origin_lng}&daddr={dest_lat},{dest_lng}"
        }
    except Exception as e:
        print(f"[DIRECTIONS ERROR] {str(e)}")
        return None


# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────

def _format_osm_places(elements, user_lat, user_lng):
    """Format OpenStreetMap results"""
    formatted = []
    for el in elements[:5]:
        # Get coordinates
        if el['type'] == 'node':
            lat = el.get('lat')
            lng = el.get('lon')
        else:
            lat = el.get('center', {}).get('lat')
            lng = el.get('center', {}).get('lon')

        tags = el.get('tags', {})
        name = tags.get('name') or tags.get('name:en') or 'Unknown'

        # Calculate distance
        distance = _calculate_distance(user_lat, user_lng, lat, lng)

        formatted.append({
            "name": name,
            "address": _get_address(tags),
            "phone": tags.get('phone') or tags.get('contact:phone', 'N/A'),
            "latitude": lat,
            "longitude": lng,
            "distance_km": round(distance, 2),
            "google_maps_link": f"https://maps.google.com/?q={lat},{lng}"
        })

    # Sort by distance
    formatted.sort(key=lambda x: x['distance_km'])
    return formatted


def _get_address(tags):
    """Build address from OSM tags"""
    parts = []
    if tags.get('addr:housenumber'):
        parts.append(tags['addr:housenumber'])
    if tags.get('addr:street'):
        parts.append(tags['addr:street'])
    if tags.get('addr:city'):
        parts.append(tags['addr:city'])
    return ', '.join(parts) if parts else 'Address not available'


def _calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km"""
    import math
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def _get_instruction(maneuver):
    """Convert OSRM maneuver to readable instruction"""
    type_ = maneuver.get('type', '')
    modifier = maneuver.get('modifier', '')
    instructions = {
        'depart': 'Start',
        'arrive': 'You have arrived',
        'turn': f'Turn {modifier}',
        'new name': f'Continue {modifier}',
        'continue': f'Continue {modifier}',
        'merge': f'Merge {modifier}',
        'roundabout': 'Enter roundabout',
        'exit roundabout': 'Exit roundabout',
    }
    return instructions.get(type_, f'{type_} {modifier}'.strip())
