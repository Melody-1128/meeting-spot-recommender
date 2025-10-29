# Intelligent Meeting Spot Recommender

**Vibe Coding Hackathon - Build Track**

## Project Description
A full-stack web application that helps friends find the fairest meeting location when they're scattered across a city. Uses intelligent algorithms and real map data to calculate optimal meeting spots based on travel time fairness.

## Features
- 🗺️ Interactive map interface for selecting friend locations
- 📍 Real-time venue search using Baidu Maps API
- ⚖️ Three sorting strategies: Total Time, Fairness, Average Time
- 🚗 Accurate travel time calculations
- 📱 Mobile-responsive design

## Technology Stack
- **Backend**: Python Flask + flask-cors + requests
- **Frontend**: Vanilla JavaScript + Leaflet.js
- **Maps API**: Baidu Maps (Place Search + Direction)
- **Algorithm**: Haversine formula for geometric center calculation

## Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd meeting-spot-recommender
```

### 2. Set up Python virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Baidu Maps API Key
Edit `app.py` and set your Baidu Maps AK:
```python
BAIDU_AK = "your_api_key_here"
```

### 5. Run the application
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## Usage
1. Click on the map to add friend locations (blue markers)
2. Select venue types (Restaurant, Café, Cinema, etc.)
3. Choose sorting strategy (Fairness recommended)
4. Adjust search radius if needed
5. Click "Find Meeting Spots"
6. View results on map and sidebar

## Project Structure
```
meeting-spot-recommender/
├── app.py              # Flask backend with API endpoints
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Main HTML page
├── static/
│   ├── css/
│   │   └── style.css  # Styling
│   └── js/
│       └── main.js    # Frontend logic
└── README.md          # This file
```

## API Endpoints

### GET /
Main application page

### GET /api/health
Health check endpoint

### POST /api/calculate-center
Calculate geometric center of coordinates

### POST /api/recommend
Get meeting spot recommendations (implemented in Phase 4)

## Development Phases
- [x] Phase 1: Project Foundation
- [ ] Phase 2: Basic Frontend
- [ ] Phase 3: Backend Core
- [ ] Phase 4: API Integration & Algorithm
- [ ] Phase 5: Full Integration & Polish

## License
MIT License - Hackathon Project

## Author
Built with AI assistance for Vibe Coding Hackathon
