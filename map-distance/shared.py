from ipyleaflet import basemaps

BASEMAPS = {
    "WorldImagery": basemaps.Esri.WorldImagery,
    "Mapnik": basemaps.OpenStreetMap.Mapnik,
    "Positron": basemaps.CartoDB.Positron,
    "DarkMatter": basemaps.CartoDB.DarkMatter,
    "NatGeoWorldMap": basemaps.Esri.NatGeoWorldMap,
    "France": basemaps.OpenStreetMap.France,
    "DE": basemaps.OpenStreetMap.DE,
}


CITIES = {
    "New York": {"latitude": 40.7128, "longitude": -74.0060, "altitude": 33},
    "London": {"latitude": 51.5074, "longitude": -0.1278, "altitude": 36},
    "Paris": {"latitude": 48.8566, "longitude": 2.3522, "altitude": 35},
    "Tokyo": {"latitude": 35.6895, "longitude": 139.6917, "altitude": 44},
    "Sydney": {"latitude": -33.8688, "longitude": 151.2093, "altitude": 39},
    "Los Angeles": {"latitude": 34.0522, "longitude": -118.2437, "altitude": 71},
    "Berlin": {"latitude": 52.5200, "longitude": 13.4050, "altitude": 34},
    "Rome": {"latitude": 41.9028, "longitude": 12.4964, "altitude": 21},
    "Beijing": {"latitude": 39.9042, "longitude": 116.4074, "altitude": 44},
    "Moscow": {"latitude": 55.7558, "longitude": 37.6176, "altitude": 156},
    "Cairo": {"latitude": 30.0444, "longitude": 31.2357, "altitude": 23},
    "Rio de Janeiro": {"latitude": -22.9068, "longitude": -43.1729, "altitude": 8},
    "Toronto": {"latitude": 43.6511, "longitude": -79.3832, "altitude": 76},
    "Dubai": {"latitude": 25.2769, "longitude": 55.2963, "altitude": 52},
    "Mumbai": {"latitude": 19.0760, "longitude": 72.8777, "altitude": 14},
    "Seoul": {"latitude": 37.5665, "longitude": 126.9780, "altitude": 38},
    "Madrid": {"latitude": 40.4168, "longitude": -3.7038, "altitude": 667},
    "Amsterdam": {"latitude": 52.3676, "longitude": 4.9041, "altitude": -2},
    "Buenos Aires": {"latitude": -34.6037, "longitude": -58.3816, "altitude": 25},
    "Stockholm": {"latitude": 59.3293, "longitude": 18.0686, "altitude": 14},
    "Boulder": {"latitude": 40.0150, "longitude": -105.2705, "altitude": 1634},
    "Lhasa": {"latitude": 29.6500, "longitude": 91.1000, "altitude": 3650},
    "Khatmandu": {"latitude": 27.7172, "longitude": 85.3240, "altitude": 1400},
}
