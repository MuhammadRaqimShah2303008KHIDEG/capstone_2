import uvicorn
from fastapi import FastAPI

from src.fuel_service.config import REDIS_HOST, REDIS_PORT
from src.fuel_service.functions import (
    data_in_redis,
    get_country_name_from_patient_location,
    get_redis_connection,
)

app = FastAPI()

redis_client = get_redis_connection(REDIS_HOST, REDIS_PORT)


@app.get("/fuel-price/{patient_lat}/{patient_long}")
def sending_fuel_prices_back_to_main_service(
    patient_lat: float, patient_long: float
) -> dict:
    """

    this function accepts two arguments patient_lat,patient_long calls
    get_country_name_from_patient_location function and then returns fuel price and currency of that country.
    Parameters:
        patient_lat (float)
        patient_long (float)
    Returns:
        Dict: value containing fuel price and currency
    """
    country = get_country_name_from_patient_location(patient_lat, patient_long)

    fuel_price, currency = data_in_redis(redis_client, country)

    return {"fuel_price": fuel_price, "currency": currency}


if __name__ == "__main__":
    # Run the FastAPI application
    uvicorn.run(app="main:app", reload=True, host="0.0.0.0", port=8001)
