/**
 * Intelligent Meeting Spot Recommender - Frontend
 * Vibe Coding Hackathon - Build Track
 */

// ============================================================================
// Global State
// ============================================================================
const state = {
    map: null,
    markers: [],
    resultMarkers: [],
    markerCounter: 0,
    maxMarkers: 10
};

// ============================================================================
// Map Initialization
// ============================================================================
function initMap() {
    // Initialize Leaflet map centered on Shanghai
    state.map = L.map('map').setView([31.2304, 121.4737], 12);
    
    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(state.map);
    
    // Add click event listener to add markers
    state.map.on('click', onMapClick);
    
    console.log('✓ Map initialized');
}

// ============================================================================
// Map Click Handler - Add Friend Location Markers
// ============================================================================
function onMapClick(e) {
    // Check if max markers reached
    if (state.markers.length >= state.maxMarkers) {
        showError(`Maximum ${state.maxMarkers} locations allowed`);
        return;
    }
    
    const { lat, lng } = e.latlng;
    
    // Create custom numbered icon
    state.markerCounter++;
    const markerNumber = state.markerCounter;
    
    const customIcon = L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            background-color: #4285f4;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
            border: 3px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        ">${markerNumber}</div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
    });
    
    // Create marker
    const marker = L.marker([lat, lng], { icon: customIcon })
        .addTo(state.map)
        .bindPopup(`
            <strong>Friend #${markerNumber}</strong><br>
            Lat: ${lat.toFixed(5)}<br>
            Lng: ${lng.toFixed(5)}<br>
            <button onclick="removeMarker(${state.markers.length})" 
                    style="margin-top: 8px; padding: 4px 12px; background: #f44336; 
                           color: white; border: none; border-radius: 4px; cursor: pointer;">
                Remove
            </button>
        `);
    
    // Store marker data
    state.markers.push({
        marker: marker,
        lat: lat,
        lng: lng,
        number: markerNumber
    });
    
    // Update UI
    updateLocationCounter();
    
    console.log(`✓ Added marker #${markerNumber} at [${lat.toFixed(5)}, ${lng.toFixed(5)}]`);
}

// ============================================================================
// Remove Individual Marker
// ============================================================================
window.removeMarker = function(index) {
    if (index >= 0 && index < state.markers.length) {
        // Remove from map
        state.map.removeLayer(state.markers[index].marker);
        
        // Remove from array
        state.markers.splice(index, 1);
        
        // Update UI
        updateLocationCounter();
        
        console.log(`✓ Removed marker at index ${index}`);
    }
};

// ============================================================================
// Clear All Markers
// ============================================================================
function clearAllMarkers() {
    // Remove all markers from map
    state.markers.forEach(item => {
        state.map.removeLayer(item.marker);
    });
    
    // Clear array
    state.markers = [];
    state.markerCounter = 0;
    
    // Update UI
    updateLocationCounter();
    hideResults();
    hideError();
    
    console.log('✓ Cleared all markers');
}

// ============================================================================
// Clear Result Markers
// ============================================================================
function clearResultMarkers() {
    state.resultMarkers.forEach(marker => {
        state.map.removeLayer(marker);
    });
    state.resultMarkers = [];
}

// ============================================================================
// Update Location Counter
// ============================================================================
function updateLocationCounter() {
    const counter = document.getElementById('locationCount');
    counter.textContent = state.markers.length;
    
    // Enable/disable search button
    const searchBtn = document.getElementById('searchBtn');
    if (state.markers.length >= 2) {
        searchBtn.disabled = false;
    } else {
        searchBtn.disabled = true;
    }
}

// ============================================================================
// Update Radius Display
// ============================================================================
function updateRadiusDisplay() {
    const slider = document.getElementById('radiusSlider');
    const display = document.getElementById('radiusValue');
    const valueInKm = (slider.value / 1000).toFixed(1);
    display.textContent = valueInKm;
}

// ============================================================================
// Get Selected Venue Types
// ============================================================================
function getSelectedVenueTypes() {
    const checkboxes = document.querySelectorAll('input[name="venueType"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// ============================================================================
// Get Selected Sort Strategy
// ============================================================================
function getSelectedSortStrategy() {
    const radio = document.querySelector('input[name="sortStrategy"]:checked');
    return radio ? radio.value : 'fair';
}

// ============================================================================
// Get Search Radius
// ============================================================================
function getSearchRadius() {
    return parseInt(document.getElementById('radiusSlider').value);
}

// ============================================================================
// Search for Meeting Spots
// ============================================================================
async function searchMeetingSpots() {
    // Validate input
    if (state.markers.length < 2) {
        showError('Please add at least 2 friend locations on the map');
        return;
    }
    
    const venueTypes = getSelectedVenueTypes();
    if (venueTypes.length === 0) {
        showError('Please select at least one venue type');
        return;
    }
    
    // Prepare request data
    const coordinates = state.markers.map(item => [item.lat, item.lng]);
    const sortStrategy = getSelectedSortStrategy();
    const radius = getSearchRadius();
    
    const requestData = {
        coordinates: coordinates,
        venue_types: venueTypes,
        sort_strategy: sortStrategy,
        radius: radius
    };
    
    console.log('🔍 Searching with params:', requestData);
    
    // Show loading
    showLoading();
    hideError();
    hideResults();
    clearResultMarkers();
    
    try {
        // Call backend API
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Search failed');
        }
        
        const data = await response.json();
        
        // Display results
        displayResults(data.results);
        
        console.log('✓ Search completed:', data);
        
    } catch (error) {
        console.error('✗ Search error:', error);
        showError(`Search failed: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// ============================================================================
// Display Results
// ============================================================================
function displayResults(results) {
    if (!results || results.length === 0) {
        showError('No meeting spots found. Try adjusting your search criteria.');
        return;
    }
    
    const resultsList = document.getElementById('resultsList');
    resultsList.innerHTML = '';
    
    results.forEach((result, index) => {
        // Create result item
        const item = document.createElement('div');
        item.className = 'result-item';
        item.onclick = () => focusOnResult(result, index);
        
        // Format travel times
        const travelTimesHtml = result.travel_times
            .map((time, i) => `Friend #${state.markers[i].number}: ${time} min`)
            .join(' • ');
        
        item.innerHTML = `
            <h4>${index + 1}. ${result.name}</h4>
            <p>📍 ${result.address}</p>
            <p><strong>⏱️ Avg Time:</strong> ${result.average_time.toFixed(1)} min</p>
            <p><strong>📊 Max Time:</strong> ${result.max_time} min</p>
            <div class="travel-times">${travelTimesHtml}</div>
        `;
        
        resultsList.appendChild(item);
        
        // Add marker to map
        addResultMarker(result, index + 1);
    });
    
    // Show results section
    showResults();
}

// ============================================================================
// Add Result Marker to Map
// ============================================================================
function addResultMarker(result, number) {
    const greenIcon = L.divIcon({
        className: 'result-marker',
        html: `<div style="
            background-color: #34a853;
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 16px;
            border: 3px solid white;
            box-shadow: 0 3px 10px rgba(0,0,0,0.4);
        ">${number}</div>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18]
    });
    
    const travelTimesHtml = result.travel_times
        .map((time, i) => `<div>Friend #${state.markers[i].number}: ${time} min</div>`)
        .join('');
    
    const marker = L.marker([result.location.lat, result.location.lng], { icon: greenIcon })
        .addTo(state.map)
        .bindPopup(`
            <div style="min-width: 200px;">
                <h4 style="margin: 0 0 8px 0; color: #34a853;">${number}. ${result.name}</h4>
                <p style="margin: 4px 0; font-size: 0.9rem;">${result.address}</p>
                <hr style="margin: 8px 0; border: none; border-top: 1px solid #ddd;">
                <div style="font-size: 0.85rem;">
                    <strong>⏱️ Average:</strong> ${result.average_time.toFixed(1)} min<br>
                    <strong>📊 Maximum:</strong> ${result.max_time} min
                </div>
                <hr style="margin: 8px 0; border: none; border-top: 1px solid #ddd;">
                <div style="font-size: 0.8rem; color: #666;">
                    ${travelTimesHtml}
                </div>
            </div>
        `);
    
    state.resultMarkers.push(marker);
}

// ============================================================================
// Focus on Result (when clicked in sidebar)
// ============================================================================
function focusOnResult(result, index) {
    const marker = state.resultMarkers[index];
    if (marker) {
        state.map.setView([result.location.lat, result.location.lng], 15);
        marker.openPopup();
    }
}

// ============================================================================
// UI Helper Functions
// ============================================================================
function showLoading() {
    document.getElementById('loadingIndicator').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

function hideError() {
    document.getElementById('errorMessage').style.display = 'none';
}

function showResults() {
    document.getElementById('resultsSection').style.display = 'block';
}

function hideResults() {
    document.getElementById('resultsSection').style.display = 'none';
}

// ============================================================================
// Event Listeners
// ============================================================================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize map
    initMap();
    
    // Clear all button
    document.getElementById('clearAllBtn').addEventListener('click', clearAllMarkers);
    
    // Search button
    document.getElementById('searchBtn').addEventListener('click', searchMeetingSpots);
    
    // Radius slider
    const slider = document.getElementById('radiusSlider');
    slider.addEventListener('input', updateRadiusDisplay);
    updateRadiusDisplay();
    
    // Initial UI state
    updateLocationCounter();
    
    console.log('✓ Application initialized');
});
