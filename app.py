"""
Intelligent Meeting Spot Recommender - Flask Backend
Hackathon Project: Build Track
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import math
import requests
from typing import List, Tuple, Dict, Optional
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Baidu Maps API Key
BAIDU_AK = "SDwo601ezFXlHnE8oMmV58II8bq52Toz"

# API Configuration
BAIDU_PLACE_API = "https://api.map.baidu.com/place/v2/search"
BAIDU_DIRECTION_API = "https://api.map.baidu.com/direction/v2/driving"

# Rate limiting
last_request_time = 0
MIN_REQUEST_INTERVAL = 0.1  # 100ms between requests


# ============================================================================
# ROUTE: Main Page
# ============================================================================
@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')


# ============================================================================
# ROUTE: Health Check
# ============================================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint for testing"""
    return jsonify({
        'status': 'ok',
        'message': 'Meeting Spot Recommender API is running',
        'baidu_api_configured': BAIDU_AK is not None
    })


# ============================================================================
# HELPER FUNCTION: Rate Limiting
# ============================================================================
def rate_limit():
    """Implement simple rate limiting for API calls"""
    global last_request_time
    current_time = time.time()
    time_since_last = current_time - last_request_time
    
    if time_since_last < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - time_since_last)
    
    last_request_time = time.time()


# ============================================================================
# HELPER FUNCTION: Haversine Distance Calculation
# ============================================================================
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth
    using the Haversine formula.
    
    Args:
        lat1, lon1: Coordinates of first point (degrees)
        lat2, lon2: Coordinates of second point (degrees)
    
    Returns:
        Distance in kilometers
    """
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    earth_radius = 6371.0
    
    return earth_radius * c


# ============================================================================
# HELPER FUNCTION: Calculate Geometric Center
# ============================================================================
def calculate_geometric_center(coordinates: List[List[float]]) -> Dict[str, float]:
    """
    Calculate the geometric center of multiple coordinates using spherical geometry.
    Handles Earth's curvature properly.
    
    Args:
        coordinates: List of [lat, lng] pairs
    
    Returns:
        Dictionary with 'lat' and 'lng' keys
    """
    if not coordinates:
        raise ValueError("Coordinates list cannot be empty")
    
    # Convert to Cartesian coordinates
    x = y = z = 0
    
    for coord in coordinates:
        lat, lng = coord
        lat_rad = math.radians(lat)
        lng_rad = math.radians(lng)
        
        x += math.cos(lat_rad) * math.cos(lng_rad)
        y += math.cos(lat_rad) * math.sin(lng_rad)
        z += math.sin(lat_rad)
    
    # Calculate average
    total = len(coordinates)
    x /= total
    y /= total
    z /= total
    
    # Convert back to spherical coordinates
    lng_center = math.atan2(y, x)
    hyp = math.sqrt(x * x + y * y)
    lat_center = math.atan2(z, hyp)
    
    return {
        'lat': math.degrees(lat_center),
        'lng': math.degrees(lng_center)
    }


# ============================================================================
# BAIDU API: Search Places
# ============================================================================
def search_places_baidu(center_lat: float, center_lng: float, 
                        query: str, radius: int, page_num: int = 0) -> Optional[List[Dict]]:
    """
    Search for places using Baidu Maps Place API
    
    Args:
        center_lat: Center latitude
        center_lng: Center longitude
        query: Search query (venue type)
        radius: Search radius in meters
        page_num: Page number for pagination (0-19)
    
    Returns:
        List of place results or None on error
    """
    try:
        rate_limit()
        
        params = {
            'query': query,
            'location': f'{center_lat},{center_lng}',
            'radius': radius,
            'output': 'json',
            'ak': BAIDU_AK,
            'page_size': 20,
            'page_num': page_num
        }
        
        print(f"   → Searching Baidu Places API: {query}")
        response = requests.get(BAIDU_PLACE_API, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"   → Baidu API Status: {data.get('status')}, Message: {data.get('message', 'OK')}")
        
        if data.get('status') == 0:
            results = data.get('results', [])
            print(f"   → Found {len(results)} results")
            return results
        else:
            print(f"   ✗ Baidu Place API error: Status {data.get('status')}, {data.get('message', 'Unknown error')}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Request error in search_places_baidu: {e}")
        return []
    except Exception as e:
        print(f"   ✗ Error in search_places_baidu: {e}")
        import traceback
        traceback.print_exc()
        return []


# ============================================================================
# BAIDU API: Calculate Travel Time
# ============================================================================
def calculate_travel_time(origin_lat: float, origin_lng: float,
                         dest_lat: float, dest_lng: float) -> Optional[int]:
    """
    Calculate driving time between two points using Baidu Direction API
    
    Args:
        origin_lat, origin_lng: Starting point coordinates
        dest_lat, dest_lng: Destination coordinates
    
    Returns:
        Travel time in minutes, or None on error
    """
    try:
        rate_limit()
        
        params = {
            'origin': f'{origin_lat},{origin_lng}',
            'destination': f'{dest_lat},{dest_lng}',
            'ak': BAIDU_AK,
            'output': 'json'
        }
        
        response = requests.get(BAIDU_DIRECTION_API, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == 0:
            routes = data.get('result', {}).get('routes', [])
            if routes:
                # Duration is in seconds, convert to minutes
                duration_seconds = routes[0].get('duration', 0)
                return round(duration_seconds / 60)
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Request error in calculate_travel_time: {e}")
        return None
    except Exception as e:
        print(f"Error in calculate_travel_time: {e}")
        return None


# ============================================================================
# SCORING ALGORITHMS
# ============================================================================
def calculate_scores(travel_times: List[int], strategy: str) -> float:
    """
    Calculate score based on travel times and selected strategy
    
    Args:
        travel_times: List of travel times in minutes
        strategy: 'total', 'fair', or 'average'
    
    Returns:
        Score value (higher is better)
    """
    if not travel_times or any(t is None for t in travel_times):
        return 0
    
    if strategy == 'total':
        # Minimize total time: score = 1 / sum(times)
        total = sum(travel_times)
        return 1000 / total if total > 0 else 0
    
    elif strategy == 'fair':
        # Minimize maximum time (most fair): score = 1 / max(times)
        max_time = max(travel_times)
        return 1000 / max_time if max_time > 0 else 0
    
    elif strategy == 'average':
        # Minimize average time: score = 1 / mean(times)
        avg_time = sum(travel_times) / len(travel_times)
        return 1000 / avg_time if avg_time > 0 else 0
    
    return 0


# ============================================================================
# MAIN RECOMMENDATION ENDPOINT
# ============================================================================
@app.route('/api/recommend', methods=['POST'])
def recommend():
    """
    Main recommendation endpoint
    
    Expected JSON body:
    {
        "coordinates": [[lat1, lng1], [lat2, lng2], ...],
        "venue_types": ["美食", "咖啡厅", ...],
        "sort_strategy": "fair",  // 'total', 'fair', or 'average'
        "radius": 3000  // in meters
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        coordinates = data.get('coordinates', [])
        venue_types = data.get('venue_types', [])
        sort_strategy = data.get('sort_strategy', 'fair')
        radius = data.get('radius', 3000)
        
        if len(coordinates) < 2:
            return jsonify({'error': 'At least 2 coordinates are required'}), 400
        
        if not venue_types:
            return jsonify({'error': 'At least one venue type is required'}), 400
        
        print(f"🔍 Processing recommendation request:")
        print(f"   - Coordinates: {len(coordinates)} locations")
        print(f"   - Venue types: {venue_types}")
        print(f"   - Strategy: {sort_strategy}")
        print(f"   - Radius: {radius}m")
        
        # Step 1: Calculate geometric center
        center = calculate_geometric_center(coordinates)
        print(f"   ✓ Center calculated: [{center['lat']:.5f}, {center['lng']:.5f}]")
        
        # Step 2: Search for places near center
        all_places = []
        for venue_type in venue_types:
            places = search_places_baidu(
                center['lat'], 
                center['lng'], 
                venue_type, 
                radius,
                page_num=0
            )
            if places:
                all_places.extend(places)
                print(f"   ✓ Found {len(places)} places for '{venue_type}'")
        
        if not all_places:
            return jsonify({
                'error': 'No venues found in this area. Try increasing the search radius.'
            }), 404
        
        print(f"   ✓ Total places found: {len(all_places)}")
        
        # Step 3: Calculate travel times for each place
        recommendations = []
        
        for place in all_places[:30]:  # Limit to 30 places to avoid timeout
            place_lat = place.get('location', {}).get('lat')
            place_lng = place.get('location', {}).get('lng')
            
            if not place_lat or not place_lng:
                continue
            
            # Calculate travel time from each friend's location
            travel_times = []
            all_times_valid = True
            
            for coord in coordinates:
                travel_time = calculate_travel_time(
                    coord[0], coord[1],
                    place_lat, place_lng
                )
                
                if travel_time is None:
                    all_times_valid = False
                    break
                
                travel_times.append(travel_time)
            
            # Skip if any travel time calculation failed
            if not all_times_valid:
                continue
            
            # Calculate score based on strategy
            score = calculate_scores(travel_times, sort_strategy)
            
            # Create recommendation object
            recommendation = {
                'name': place.get('name', 'Unknown'),
                'address': place.get('address', 'No address'),
                'location': {
                    'lat': place_lat,
                    'lng': place_lng
                },
                'travel_times': travel_times,
                'total_time': sum(travel_times),
                'average_time': sum(travel_times) / len(travel_times),
                'max_time': max(travel_times),
                'score': score
            }
            
            recommendations.append(recommendation)
        
        if not recommendations:
            return jsonify({
                'error': 'Could not calculate travel times. Please try again.'
            }), 500
        
        # Step 4: Sort by score and return top 5
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        top_recommendations = recommendations[:5]
        
        print(f"   ✓ Calculated {len(recommendations)} valid recommendations")
        print(f"   ✓ Returning top 5 results")
        
        return jsonify({
            'success': True,
            'results': top_recommendations,
            'center': center,
            'total_found': len(recommendations)
        })
    
    except Exception as e:
        print(f"✗ Error in recommend endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Server error: {str(e)}'
        }), 500


# ============================================================================
# ROUTE: Calculate Center (Test Endpoint)
# ============================================================================
@app.route('/api/calculate-center', methods=['POST'])
def calculate_center():
    """
    Test endpoint to verify geometric center calculation
    
    Expected JSON body:
    {
        "coordinates": [[lat1, lng1], [lat2, lng2], ...]
    }
    """
    try:
        data = request.get_json()
        coordinates = data.get('coordinates', [])
        
        if not coordinates or len(coordinates) < 2:
            return jsonify({
                'error': 'At least 2 coordinates are required'
            }), 400
        
        center = calculate_geometric_center(coordinates)
        
        return jsonify({
            'success': True,
            'center': center,
            'input_count': len(coordinates)
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


# ============================================================================
# Main Entry Point
# ============================================================================
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Intelligent Meeting Spot Recommender - Starting")
    print("=" * 60)
    print(f"✓ Baidu Maps API Key configured: {BAIDU_AK[:10]}...")
    print(f"✓ Server starting on http://0.0.0.08000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=8000)
