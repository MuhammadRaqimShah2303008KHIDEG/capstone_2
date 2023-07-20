from typing import Tuple

import redis  # type:ignore
import requests  # type:ignore
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim

from src.fuel_service.config import FUEL_URL


def get_redis_connection(redis_host: str, redis_port: int) -> redis.Redis:
    """
    The function creates the redis connection.
    Parameters:
        redis_host (str)
        redis_port (int)
    Returns:
        redis.Redis: connection.
    """
    return redis.Redis(host=redis_host, port=redis_port, db=0)


def get_country_name_from_patient_location(
    patients_lat: float, patients_long: float
) -> str:
    """
    The function calls geolocator.reverse function that takes latitude and
    longitude which are coming from the main service.
    Parameters:
        patients_lat (float)
        patients_long (float)
    Returns:
        Dict: containing name of the country on the basis of patients_latitude and patients_longitude.
    """
    geolocator = Nominatim(user_agent="Get Country")
    location = geolocator.reverse(
        f"{patients_lat},{patients_long}",
        exactly_one=True,
        language="en",
    )
    if location is not None and "address" in location.raw:
        address = location.raw["address"]
        country = address.get("country", "").replace(" ", "-")
    else:
        raise LookupError(
            f"Country not found for lat {patients_lat} and long {patients_long}"
        )
    return country


def scrapping_from_url(redis_client: redis.Redis, country: str) -> Tuple[float, str]:
    """
    The function scraps data from a webpage accepting country as an argument
    and then saves the fuel prices and currency in redis.
    Parameters:
        redis_client (redis.Redis)
        country (str)
    """
    fuel_prices_url = f"{FUEL_URL}{country}/gasoline_prices/"
    fuel_prices_response = requests.get(fuel_prices_url)
    fuel_prices_response.raise_for_status()
    html_content = fuel_prices_response.content
    soup = BeautifulSoup(html_content, "html.parser")
    div = soup.find("div", {"id": "graphPageLeft"})
    if table := div.find("table"):
        rows = table.find_all("tr")
        if len(rows) > 1:
            fuel_price = rows[1].find_all("td")[0].text.strip()
            currency_name = rows[1].find_all("th")[0].text.strip()
            redis_client.set(country, f"{fuel_price}:{currency_name}")
            seconds_in_24h = 24 * 60 * 60
            redis_client.expire(country, seconds_in_24h)
        else:
            return float("nan"), "N/A"
    else:
        return float("nan"), "N/A"
    return float(fuel_price), currency_name


def data_in_redis(redis_client: redis.Redis, country: str) -> Tuple[float, str]:
    """
    The function gets data of a specific country from redis if the
    data exists if not then it calls the scrapping_from_url function.
    Parameters:
        redis_client (redis.Redis)
        country (str)
    Returns:
        tuple: value of fuel_price and currency
    """
    if country is None or country == "":
        # Return default values if country is None or empty
        return float("nan"), "N/A"
    if redis_client.exists(country):
        if (redis_data := redis_client.get(country)) is not None:
            redis_data = redis_data.decode()
            fuel_price, currency = redis_data.split(":")
            return float(fuel_price), currency
    else:
        fuel_price, currency_name = scrapping_from_url(redis_client, country)
        return float(fuel_price), currency_name
    # Return default values if fuel price and currency are not available
    return float("nan"), "N/A"
