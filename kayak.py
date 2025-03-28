def kayak_search(loc: str, pickup: str, dropoff: str) -> str:
    """
    Generates a Kayak URL for car rentals between two locations and dates.
    
    Args:
        loc: Location string in format "from-to-destination"
        pickup: Pickup date in YYYY-MM-DD format
        dropoff: Return date in YYYY-MM-DD format
    """
    clean_location = loc.lower().replace(' ', '-')
    URL = f"https://www.kayak.com/cars/{clean_location}/{pickup}/{dropoff}?sort=price_a"
    return URL
