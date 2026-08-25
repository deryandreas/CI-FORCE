import requests

IQAIR_API_KEY = "c7221a94-83e0-42f3-920b-0b5e71c0603e"

def get_iqair_weather():
    """
    Mengambil data suhu dan kelembapan real-time dari IQAir API.
    """
    url = f"https://api.airvisual.com/v2/nearest_city?key={IQAIR_API_KEY}"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get("status") == "success":
            city_data = data.get("data", {})
            current = city_data.get("current", {})
            weather = current.get("weather", {})
            
            suhu = weather.get("tp", 32)
            kelembapan = weather.get("hu", 33)
            kota = city_data.get("city", "Bandung")
            
            resiko = "Risiko Korosi Tinggi" if kelembapan > 75 else "Kondisi Aman / Stabil"
            
            return {
                "kota": kota,
                "suhu": suhu,
                "kelembapan": kelembapan,
                "resiko": resiko,
            }
        else:
            print(f"[IQAir Error]: {data.get('data', {}).get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"[IQAir Connection Error]: {e}")
        
    # Fallback jika request gagal atau offline
    return {
        "kota": "Bandung",
        "suhu": 32,
        "kelembapan": 33,
        "resiko": "Kondisi Aman / Stabil (Offline)",
    }