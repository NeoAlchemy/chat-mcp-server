import httpx
import base64
import time
from typing import Any
from pathlib import Path
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from typing import List, Dict, Any


from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from mcp import types

# Initialize FastMCP server
mcp = FastMCP("Activity")

# === Configuration ===
BOOK_PATH = "Activities.csv"
BOOK_URI  = f"file://{BOOK_PATH}"

# === Tools ===

@mcp.tool(name="suggest_activities_under_price", description="Suggests activities where total family cost is under the given price.")
def suggest_activities_under_price(
    max_price: float,
    family: Dict[str, Any],
    all_activities: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Suggests activities where total family cost is under the given price.

    Args:
        max_price (float): Maximum allowed price.
        family (dict): Family structure with number of adults and list of children and thier ages.
        all_activities (list): List of activity dicts from resource (CSV or JSON).

    Returns:
        dict: Summary of filtered activity suggestions under the budget.
    """

    suggestions = []

    for activity in all_activities:
        try:
            base_price = float(activity.get("Base Price", 0))
            child_price = float(activity.get("Price Per Child", 0))
            adult_price = float(activity.get("Price Per Adult", 0))

            min_age = int(activity.get("Min Age", 0))
            max_age = int(activity.get("Max Age", 99))

            # Check if all children are within age range
            eligible = all(min_age <= child["age"] <= max_age for child in family.get("children", []))
            if not eligible:
                continue

            # Count family members
            num_kids = len(family.get("children", []))
            num_adults = family.get("adults", 0)

            # Calculate total cost
            total_price = base_price + (child_price * num_kids) + (adult_price * num_adults)

            # Filter by budget
            if total_price <= max_price:
                suggestions.append({
                    "activity": activity.get("Activity Name"),
                    "total_price": total_price,
                    "location": activity.get("Location"),
                    "breakdown": {
                        "base": base_price,
                        "adults": {
                            "count": num_adults,
                            "rate": adult_price,
                            "subtotal": adult_price * num_adults
                        },
                        "children": {
                            "count": num_kids,
                            "rate": child_price,
                            "subtotal": child_price * num_kids
                        }
                    }
                })

        except (ValueError, TypeError):
            # Handle missing or malformed data
            continue

    return {
        "status": "success",
        "max_price": max_price,
        "count": len(suggestions),
        "results": suggestions
    }

def geocode_address(address: str):
    try:
        time.sleep(1)  # Nominatim requires respectful delays
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
    except Exception as e:
        print(f"Geocoding failed for '{address}': {e}")
    return None

@mcp.tool(name="distance_from_house", description="Returns a list of activities sorted by distance from the user's home.")
def distance_from_house(home_address: str, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Returns a list of activities sorted by distance from the user's home.

    Use this tool when a user asks for nearby events or activities, or when the request includes keywords like:
    "close to me", "nearby", "within X miles", or specifies a location like a home address or city.

    The tool calculates the driving distance (in kilometers) between the user's provided home address and each activity's location.

    Inputs:
    - home_address (string): The full address or city/town the user is located at or wants to start from.

    Outputs:
    - A dictionary with:
        - `home`: the address used for comparison
        - `results`: list of activity entries with:
            - activity name
            - location (address)
            - distance_km (float): rounded to 2 decimal places

    Typical use cases:
    - "What are some weekend activities near me?"
    - "Find events within 20 km of Springfield."
    - "Anything we can do that’s close to our house?"

    Do not use this tool if the user's location is unknown or ambiguous.
    """
    home_coords = geocode_address(home_address)
    if not home_coords:
        return {"status": "error", "message": "Could not geocode home address"}

    results = []

    for activity in activities:
        activity_address = activity.get("Location")
        if not activity_address:
            continue

        activity_coords = geocode_address(activity_address)
        if not activity_coords:
            continue

        distance_km = geodesic(home_coords, activity_coords).km
        results.append({
            "activity": activity.get("Activity Name"),
            "location": activity_address,
            "distance_km": round(distance_km, 2)
        })

    return {
        "status": "success",
        "home": home_address,
        "count": len(results),
        "results": sorted(results, key=lambda x: x["distance_km"])
    }   

# === Resource ===
@mcp.resource(BOOK_URI)
async def get_book() -> str:
    raw = Path(BOOK_PATH).read_text()
    return raw

# === Prompts ====
@mcp.prompt()
def family_activites_near_me() -> list[base.Message]:
    return [
        base.UserMessage("What are some activities that me and my wife who are both 45 can do. This needs to be 15 miles near Keller, TX.")
    ]

@mcp.prompt()
def family_activites_under_100() -> str:
    return [
        base.UserMessage("What are some activities that my wife and I who are both 45 can do that are free?")
    ]