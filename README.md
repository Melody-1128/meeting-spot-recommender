# meeting-spot-recommender
# This project is for vibe coding competition. It's my first time to try to start and create a web, also my first time to use Github. I want to develop a function that helps multuple people find a central meeting place.
# Intelligent Meeting Spot Recommender

**Vibe Coding Hackathon - Build Track**

A full-stack web application that helps friends find the fairest meeting location when scattered across a city, using real-time map data and intelligent algorithms.

---

## 🎯 Overview

Finding a fair meeting spot for friends at different locations can be challenging. This app solves that by:
- Calculating the geometric center of all participants
- Searching nearby venues using Baidu Maps API
- Computing actual travel times for each person
- Recommending top 5 spots based on fairness strategies

---

## ✨ Features

- 🗺️ **Interactive Map**: Click to add locations, visual markers for participants and results
- 📍 **Smart Search**: Filter by venue type (Restaurant, Café, Cinema, Park, Mall)
- ⚖️ **3 Sorting Strategies**: Total Time, Most Fair, Average Time
- 🚗 **Real Travel Times**: Actual driving time calculations
- 📱 **Responsive Design**: Works on desktop and mobile

---

## 🛠️ Tech Stack

**Backend**: Python Flask + flask-cors + requests  
**Frontend**: Vanilla JavaScript + Leaflet.js  
**APIs**: Baidu Maps (Place Search + Direction)  
**Algorithm**: Haversine formula for geometric calculations

---

## 📁 Project Structure

```
meeting-spot-recommender/
├── app.py              # Flask backend
├── requirements.txt    # Dependencies
├── templates/
│   └── index.html     # Main page
└── static/
    ├── css/style.css  # Styling
    └── js/main.js     # Frontend logic
```

---

## 🚀 Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

### Usage

1. Open `http://localhost:8000` in browser
2. Click map to add 2-10 friend locations (blue markers)
3. Select venue types and sorting strategy
4. Click "Find Meeting Spots"
5. View results (green markers) on map and sidebar

---

## 🔧 API Endpoints

**GET /** - Main application page  
**GET /api/health** - Health check  
**POST /api/recommend** - Get meeting spot recommendations

### Example Request
```json
{
  "coordinates": [[31.2304, 121.4737], [31.2244, 121.4692]],
  "venue_types": ["美食", "咖啡厅"],
  "sort_strategy": "fair",
  "radius": 3000
}
```

---

## 🧮 Algorithm

### Geometric Center
Uses spherical geometry to calculate true center on Earth's surface

### Haversine Formula
Calculates great-circle distance between coordinates
```
distance = R × 2 × atan2(√a, √(1-a))
where a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
```

### Scoring Strategies
- **Total Time**: `score = 1000 / sum(times)`
- **Most Fair**: `score = 1000 / max(times)` ← Recommended
- **Average Time**: `score = 1000 / mean(times)`

---

## 🐛 Troubleshooting

**Port in use**: Change port in `app.py` last line  
**No results**: Ensure markers in Shanghai area, increase radius  
**API errors**: Check API key, internet connection

---


## 📊 Key Metrics

- Response Time: < 5 seconds
- Max Locations: 10 participants
- Results: Top 5 recommendations
- API Rate Limit: 100ms interval

---

## 📄 License

MIT License - Hackathon Project

---

**Built with AI assistance (Claude) for Vibe Coding Hackathon**
