import os, requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("USDA_API_KEY")

def usda_search_energy_kcal(query: str):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"query": query, "pageSize": 1, "api_key": API_KEY}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    if not data.get("foods"): return None
    item = data["foods"][0]
    desc = item.get("description", "Unknown")
    kcal = None
    for n in item.get("foodNutrients", []):
        name, unit = n.get("nutrientName", "").lower(), n.get("unitName", "").lower()
        if "energy" in name and unit in ("kcal", "kcal/d"):
            kcal = n.get("value"); break
    return (desc, kcal)
