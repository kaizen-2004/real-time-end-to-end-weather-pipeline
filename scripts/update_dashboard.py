import os
import requests
from datetime import datetime

API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')

CITIES = [
    {"city_id": 1701668, "name": "Manila", "lat": 14.5995, "lon": 120.9842},
    {"city_id": 1687110, "name": "Cebu City", "lat": 10.3157, "lon": 123.8854},
    {"city_id": 711713, "name": "Davao City", "lat": 7.1907, "lon": 125.4553},
    {"city_id": 1704068, "name": "Makati", "lat": 14.5547, "lon": 121.0500},
    {"city_id": 1694282, "name": "Quezon City", "lat": 14.6760, "lon": 121.0437},
]

def fetch_weather():
    weather_data = []
    for city in CITIES:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={city['lat']}&lon={city['lon']}&appid={API_KEY}&units=metric"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            weather_data.append({
                "city": city["name"],
                "lat": city["lat"],
                "lon": city["lon"],
                "temp": round(data["main"]["temp"]),
                "feels_like": round(data["main"]["feels_like"]),
                "humidity": data["main"]["humidity"],
                "wind": round(data["wind"]["speed"] * 3.6),
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"].title(),
            })
        except Exception as e:
            print(f"Error fetching {city['name']}: {e}")
            weather_data.append({
                "city": city["name"],
                "lat": city["lat"],
                "lon": city["lon"],
                "temp": 0,
                "feels_like": 0,
                "humidity": 0,
                "wind": 0,
                "condition": "Unknown",
                "description": "Data unavailable",
            })
    return weather_data

def generate_html(weather_data):
    temps = [w["temp"] for w in weather_data]
    humidities = [w["humidity"] for w in weather_data]
    avg_temp = round(sum(temps) / len(temps), 1)
    avg_humidity = round(sum(humidities) / len(humidities))
    max_temp = max(temps)
    min_temp = min(temps)
    temp_range = max_temp - min_temp
    hottest = next(w for w in weather_data if w["temp"] == max_temp)
    coolest = next(w for w in weather_data if w["temp"] == min_temp)
    conditions = list(set(w["condition"] for w in weather_data))
    max_humidity = max(humidities)
    most_humid = next(w for w in weather_data if w["humidity"] == max_humidity)
    rainy = [w["city"] for w in weather_data if "rain" in w["condition"].lower()]
    
    now = datetime.now().strftime("%I:%M %p")
    
    weather_json = str(weather_data).replace("'", '"')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Philippine Weather Pipeline</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #0a0a1a; color: #e0e0e0; min-height: 100vh; overflow-x: hidden; width: 100%; }}

        .header {{ padding: 16px 32px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.06); flex-wrap: wrap; gap: 8px; }}
        .header h1 {{ font-size: 1.2rem; font-weight: 600; color: #fff; }}
        .header h1 span {{ color: #64ffda; }}
        .header-meta {{ text-align: right; color: #555; font-size: 0.8rem; }}

        .problem-section {{ padding: 24px 32px; background: rgba(100,255,218,0.03); border-bottom: 1px solid rgba(255,255,255,0.06); }}
        .problem-label {{ font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; color: #64ffda; margin-bottom: 8px; }}
        .problem-text {{ font-size: 1rem; color: #b0b0b0; line-height: 1.6; max-width: 900px; }}
        .problem-text strong {{ color: #fff; }}

        .main {{ padding: 24px 32px; overflow: hidden; }}

        .section-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }}
        .section-num {{ background: #64ffda; color: #0a0a1a; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; flex-shrink: 0; }}
        .section-title {{ font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; color: #888; }}
        .section-answer {{ font-size: 0.9rem; color: #64ffda; margin-left: auto; white-space: nowrap; }}

        .kpi-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 32px; }}
        .kpi {{ background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 16px; }}
        .kpi-label {{ color: #555; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.5px; }}
        .kpi-value {{ font-size: 1.4rem; font-weight: 700; color: #fff; margin-top: 4px; }}
        .kpi-sub {{ color: #64ffda; font-size: 0.75rem; margin-top: 4px; }}

        .map-container {{ background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; overflow: hidden; margin-bottom: 32px; }}
        .map-header {{ padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center; }}
        .map-header h3 {{ font-size: 0.85rem; color: #fff; font-weight: 500; }}
        .map-legend {{ display: flex; gap: 12px; font-size: 0.7rem; }}
        .legend-item {{ display: flex; align-items: center; gap: 4px; color: #666; }}
        .legend-dot {{ width: 8px; height: 8px; border-radius: 50%; }}
        #map {{ height: 320px; }}

        .city-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin-bottom: 32px; }}
        .city-card {{ background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 16px; text-align: center; transition: border-color 0.2s; }}
        .city-card:hover {{ border-color: rgba(100,255,218,0.3); }}
        .city-name {{ font-size: 0.8rem; color: #666; margin-bottom: 6px; }}
        .city-temp {{ font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }}
        .city-condition {{ font-size: 0.7rem; color: #555; }}
        .city-detail {{ font-size: 0.65rem; color: #444; margin-top: 6px; }}

        .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; margin-bottom: 32px; }}
        .chart-card {{ background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 16px; min-width: 0; }}
        .chart-card h4 {{ font-size: 0.8rem; color: #666; margin-bottom: 12px; font-weight: 500; }}
        .chart-container {{ height: 220px; position: relative; width: 100%; }}

        .insights-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 32px; }}
        .insight-card {{ background: rgba(100,255,218,0.04); border: 1px solid rgba(100,255,218,0.15); border-radius: 8px; padding: 16px; }}
        .insight-card h5 {{ font-size: 0.75rem; color: #64ffda; margin-bottom: 6px; font-weight: 500; }}
        .insight-card p {{ font-size: 0.8rem; color: #888; line-height: 1.5; }}

        .pipeline-status {{ display: flex; gap: 24px; padding: 16px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; margin-bottom: 32px; flex-wrap: wrap; }}
        .status-item {{ display: flex; align-items: center; gap: 8px; }}
        .status-dot {{ width: 8px; height: 8px; border-radius: 50%; background: #64ffda; }}
        .status-label {{ font-size: 0.75rem; color: #666; }}
        .status-value {{ font-size: 0.75rem; color: #fff; }}

        .footer {{ padding: 16px 32px; border-top: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center; color: #333; font-size: 0.75rem; flex-wrap: wrap; gap: 8px; }}
        .footer a {{ color: #64ffda; text-decoration: none; }}

        .leaflet-popup-content-wrapper {{ background: #1a1a2e; color: #fff; border-radius: 6px; border: 1px solid rgba(100,255,218,0.2); }}
        .leaflet-popup-tip {{ background: #1a1a2e; }}
        .popup-content {{ text-align: center; padding: 4px; }}
        .popup-city {{ font-weight: 600; font-size: 0.9rem; margin-bottom: 4px; }}
        .popup-temp {{ font-size: 1.3rem; color: #64ffda; font-weight: 700; }}
        .popup-details {{ color: #888; font-size: 0.75rem; margin-top: 6px; }}
        .dark-tooltip {{ background: #1a1a2e !important; color: #fff !important; border: 1px solid #64ffda !important; border-radius: 3px !important; font-size: 0.75rem !important; }}
    </style>
</head>
<body>
    <div class="header">
        <h1><span>PH</span> Weather Pipeline</h1>
        <div class="header-meta">
            Last updated: {now}<br>
            Auto-refresh every 30 min
        </div>
    </div>

    <div class="problem-section">
        <div class="problem-label">Problem Statement</div>
        <div class="problem-text">
            Weather data across the <strong>Philippine archipelago varies significantly by region</strong>. 
            No automated pipeline existed to collect, transform, and visualize real-time weather data 
            for multiple cities in a <strong>structured, analytics-ready format</strong>.
        </div>
    </div>

    <div class="main">
        <div class="section-header">
            <div class="section-num">1</div>
            <div class="section-title">What is the weather right now across Philippine cities?</div>
            <div class="section-answer">{avg_temp}C average, ranging from {min_temp}C to {max_temp}C</div>
        </div>

        <div class="kpi-row">
            <div class="kpi">
                <div class="kpi-label">Average Temperature</div>
                <div class="kpi-value">{avg_temp}C</div>
                <div class="kpi-sub">Range: {temp_range}C spread</div>
            </div>
            <div class="kpi">
                <div class="kpi-label">Hottest City</div>
                <div class="kpi-value">{max_temp}C</div>
                <div class="kpi-sub">{hottest["city"]}</div>
            </div>
            <div class="kpi">
                <div class="kpi-label">Coolest City</div>
                <div class="kpi-value">{min_temp}C</div>
                <div class="kpi-sub">{coolest["city"]}</div>
            </div>
            <div class="kpi">
                <div class="kpi-label">Avg Humidity</div>
                <div class="kpi-value">{avg_humidity}%</div>
                <div class="kpi-sub">across all cities</div>
            </div>
        </div>

        <div class="map-container">
            <div class="map-header">
                <h3>Geographic Distribution</h3>
                <div class="map-legend">
                    <div class="legend-item"><div class="legend-dot" style="background:#ff6b6b"></div> 32C+</div>
                    <div class="legend-item"><div class="legend-dot" style="background:#feca57"></div> 30-31C</div>
                    <div class="legend-item"><div class="legend-dot" style="background:#48dbfb"></div> 28-29C</div>
                    <div class="legend-item"><div class="legend-dot" style="background:#64ffda"></div> Below 28C</div>
                </div>
            </div>
            <div id="map"></div>
        </div>

        <div class="city-grid" id="city-grid"></div>

        <div class="section-header">
            <div class="section-num">2</div>
            <div class="section-title">How do cities compare to each other?</div>
            <div class="section-answer">{hottest["city"]} is {temp_range}C warmer than {coolest["city"]}</div>
        </div>

        <div class="charts-grid">
            <div class="chart-card">
                <h4>Temperature Comparison</h4>
                <div class="chart-container"><canvas id="tempChart"></canvas></div>
            </div>
            <div class="chart-card">
                <h4>Humidity Levels</h4>
                <div class="chart-container"><canvas id="humidityChart"></canvas></div>
            </div>
        </div>

        <div class="section-header">
            <div class="section-num">3</div>
            <div class="section-title">What patterns and insights emerge from the data?</div>
            <div class="section-answer">{len(conditions)} different conditions across 5 cities</div>
        </div>

        <div class="insights-grid">
            <div class="insight-card">
                <h5>Regional Variation</h5>
                <p>Temperature varies by {temp_range}C across the archipelago. {hottest["city"]} leads at {max_temp}C, while {coolest["city"]} is coolest at {min_temp}C.</p>
            </div>
            <div class="insight-card">
                <h5>Humidity Pattern</h5>
                <p>{most_humid["city"]} has the highest humidity at {max_humidity}%. {"Rain is currently falling in " + " and ".join(rainy) + "." if rainy else "All cities are currently dry."}</p>
            </div>
            <div class="insight-card">
                <h5>Weather Diversity</h5>
                <p>{", ".join(conditions)}. The archipelago's geography creates distinct microclimates across regions.</p>
            </div>
            <div class="insight-card">
                <h5>Live Data</h5>
                <p>Data sourced from OpenWeatherMap API and refreshed every 30 minutes via GitHub Actions.</p>
            </div>
        </div>

        <div class="section-header">
            <div class="section-num">4</div>
            <div class="section-title">Is the pipeline delivering fresh, reliable data?</div>
        </div>

        <div class="pipeline-status">
            <div class="status-item">
                <div class="status-dot"></div>
                <div class="status-label">Pipeline</div>
                <div class="status-value">Active</div>
            </div>
            <div class="status-item">
                <div class="status-dot"></div>
                <div class="status-label">Schedule</div>
                <div class="status-value">Every 30 min</div>
            </div>
            <div class="status-item">
                <div class="status-dot"></div>
                <div class="status-label">Cities</div>
                <div class="status-value">5 tracked</div>
            </div>
            <div class="status-item">
                <div class="status-dot"></div>
                <div class="status-label">Data Source</div>
                <div class="status-value">OpenWeatherMap API</div>
            </div>
            <div class="status-item">
                <div class="status-dot"></div>
                <div class="status-label">Last Updated</div>
                <div class="status-value">{now}</div>
            </div>
        </div>
    </div>

    <div class="footer">
        <div>Built by <a href="https://steve-villa-devportfolio.netlify.app/" target="_blank">Steve A. Villa</a> | Data: OpenWeatherMap API | Stack: Airflow + PostgreSQL + dbt + Snowflake</div>
        <div><a href="https://github.com/kaizen-2004/real-time-end-to-end-weather-pipeline" target="_blank">GitHub</a></div>
    </div>

    <script>
        const weatherData = {weather_json};

        function getMarkerColor(temp) {{
            if (temp >= 32) return '#ff6b6b';
            if (temp >= 30) return '#feca57';
            if (temp >= 28) return '#48dbfb';
            return '#64ffda';
        }}

        function initMap() {{
            const map = L.map('map', {{ zoomControl: false }}).setView([12.8797, 121.7740], 6);
            L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                attribution: 'OpenStreetMap, CARTO', maxZoom: 19
            }}).addTo(map);

            weatherData.forEach(city => {{
                const marker = L.circleMarker([city.lat, city.lon], {{
                    radius: 18, fillColor: getMarkerColor(city.temp), color: '#fff', weight: 2, fillOpacity: 0.9
                }}).addTo(map);

                marker.bindPopup(`
                    <div class="popup-content">
                        <div class="popup-city>${{city.city}}</div>
                        <div class="popup-temp>${{city.temp}}C</div>
                        <div class="popup-details>${{city.description}}<br>Feels ${{city.feels_like}}C | ${{city.humidity}}% | ${{city.wind}}km/h</div>
                    </div>
                `);
                marker.bindTooltip(city.city, {{ permanent: true, className: 'dark-tooltip', direction: 'top', offset: [0, -12] }});
            }});
        }}

        function renderCityCards() {{
            document.getElementById('city-grid').innerHTML = weatherData.map(city => `
                <div class="city-card">
                    <div class="city-name>${{city.city}}</div>
                    <div class="city-temp" style="color: ${{getMarkerColor(city.temp)}}">${{city.temp}}C</div>
                    <div class="city-condition>${{city.description}}</div>
                    <div class="city-detail>Feels ${{city.feels_like}}C | ${{city.humidity}}% | ${{city.wind}}km/h</div>
                </div>
            `).join('');
        }}

        function initCharts() {{
            new Chart(document.getElementById('tempChart'), {{
                type: 'bar',
                data: {{
                    labels: weatherData.map(d => d.city),
                    datasets: [{{ data: weatherData.map(d => d.temp), backgroundColor: weatherData.map(d => getMarkerColor(d.temp)), borderRadius: 4, barThickness: 28 }}]
                }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ min: 20, max: 40, grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#555' }} }}, x: {{ grid: {{ display: false }}, ticks: {{ color: '#555' }} }} }} }}
            }});

            new Chart(document.getElementById('humidityChart'), {{
                type: 'bar',
                data: {{
                    labels: weatherData.map(d => d.city),
                    datasets: [{{ data: weatherData.map(d => d.humidity), backgroundColor: 'rgba(100, 255, 218, 0.5)', borderRadius: 4, barThickness: 28 }}]
                }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ min: 50, max: 100, grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#555' }} }}, x: {{ grid: {{ display: false }}, ticks: {{ color: '#555' }} }} }} }}
            }});
        }}

        renderCityCards();
        initMap();
        initCharts();
    </script>
</body>
</html>'''
    return html

if __name__ == "__main__":
    print("Fetching live weather data...")
    data = fetch_weather()
    print(f"Got data for {len(data)} cities")
    
    html = generate_html(data)
    
    with open("index.html", "w") as f:
        f.write(html)
    
    print("Dashboard updated with live data!")
