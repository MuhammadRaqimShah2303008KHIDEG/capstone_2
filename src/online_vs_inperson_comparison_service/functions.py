import requests  # type: ignore
from transport_co2 import estimate_co2
from src.online_vs_inperson_comparison_service.config import (
    ACCOUNT_URL,
    API_KEY,
    COUNCILLOR_URL,
    PATIENT_URL,
    ROUTE_URL,
    GOOGLE_GEO_API,
    GOOGLE_GEO_API_KEY
)


def get_data_from_url(url: str) -> dict:
    """
    This function fetches data from an API using the provided URL.

    Parameters:
        url (str): URL to fetch data from.

    Returns:
        json(dict): JSON data retrieved from the API.

    """

    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for non-200 status codes
    return response.json()


def get_location_data(patient_or_councillor_id: int, is_patient: bool) -> dict:
    """
    This function retrieves location data for either a patient or a councillor.
    Extracts the user_id from the retrieved data and accesses the relevant information from the account data.
    Assumes the account data is in JSON format and navigates the nested structure to extract latitude, longitude,
    and region information.
    Parameters:
        patient_or_councillor_id (int): ID of the patient or councillor.
        is_patient (bool): Indicates whether the data is for a patient (True) or a councillor (False).
    Returns:
        dict: Dictionary with location data, including latitude, longitude, and region.
    """
    if is_patient:
        data = get_data_from_url(f"{PATIENT_URL}{patient_or_councillor_id}")
    else:
        data = get_data_from_url(f"{COUNCILLOR_URL}{patient_or_councillor_id}")
    user_id = data["userId"]
    account_data = get_data_from_url(f"{ACCOUNT_URL}{user_id}")
    address = account_data["address"]
    return address



def get_coordinates(address):
    response = requests.get(f"{GOOGLE_GEO_API}?address={address}&key={GOOGLE_GEO_API_KEY}")
    response = response.json()
    latitude = response["results"][0]["geometry"]["location"]["lat"]
    longitude = response["results"][0]["geometry"]["location"]["lng"]
    return latitude, longitude


def get_distance_time_from_tomtom(
    patient_lat: float,
    patient_long: float,
    councillor_lat: float,
    councillor_long: float,
) -> dict:
    """
    this function calculates the distance between patient and councillor on the bases of thier latitude and longitude
    by using tomtom distance api

    Parameters:
        patient_lat (float):patient latitude
        patient_long (float):patient longitude
        councillor_lat (float):councillor latitude
        councillor_long (float):councillor longitude

    Result:
       dict: values containing for distance in km , time in min
    """
    route_data = get_data_from_url(
        f"{ROUTE_URL}{patient_lat},{patient_long}:{councillor_lat},{councillor_long}/json?key={API_KEY}"
    )

    distance = float(route_data["routes"][0]["summary"]["lengthInMeters"]) / 1000
    time = float(route_data["routes"][0]["summary"]["travelTimeInSeconds"]) / 60
    rounded_distance = round(distance, 3)
    rounded_time = round(time, 3)

    distance_time = {"distance": rounded_distance, "time": rounded_time}

    return distance_time


def calculate_savings(
    distance: float, fuel_price: float, avg_fuel_consumption: float = 6.5
) -> dict:
    """
    this function calculates the total cost, co2 saved and methane saved with respect to distance and
    considering that subject is driving a car which has an average fuel consumption of `avg_fuel_consumption`.

    Parameters:
        distance (float)
        fuel_price (float)
        avg_fuel_consumption (float)

    Result:
       dict: values containing for total_cost,co2_saved and methane_saved
    """
    total_cost = (distance / avg_fuel_consumption) * float(fuel_price)
    methane_emission_factor = 0.001  # Methane emission factor in kg/L
    co2_saved = estimate_co2(mode="car", distance_in_km=distance)
    methane_saved = (distance / avg_fuel_consumption) * methane_emission_factor
    result = {
        "total_cost": total_cost,
        "co2_saved": co2_saved,
        "methane_saved": methane_saved,
    }
    return result
