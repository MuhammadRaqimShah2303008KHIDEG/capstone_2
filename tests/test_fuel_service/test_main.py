from unittest import TestCase, mock

from fastapi.testclient import TestClient

from src.fuel_service.functions import get_redis_connection
from src.fuel_service.main import app


class TestRedisConnection(TestCase):
    @mock.patch("src.fuel_service.functions.redis.Redis")
    def test_get_redis_connection(self, mock_redis):
        redis_host = "localhost"
        redis_port = 6379
        connection = get_redis_connection(redis_host, redis_port)
        mock_redis.assert_called_once_with(host=redis_host, port=redis_port, db=0)
        self.assertEqual(connection, mock_redis.return_value)


class TestFuelPriceApi(TestCase):
    client = TestClient(app)

    @mock.patch("src.fuel_service.main.get_country_name_from_patient_location")
    @mock.patch("src.fuel_service.main.data_in_redis")
    def test_sending_fuel_prices_back_to_main_service(
        self,
        mock_data_in_redis,
        mock_get_country,
    ):
        mock_get_country.return_value = "Pakistan"
        mock_data_in_redis.return_value = (262.000, "PKR")

        response = self.client.get("/fuel-price/24.8/67.0")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"fuel_price": 262.0, "currency": "PKR"},
        )

        mock_get_country.assert_called_once_with(24.8, 67.0)
        mock_data_in_redis.assert_called_once_with(mock.ANY, "Pakistan")

    @mock.patch("src.fuel_service.main.get_country_name_from_patient_location")
    @mock.patch("src.fuel_service.main.data_in_redis")
    def test_sending_fuel_prices_back_to_main_service_with_exception(
        self, mock_data_in_redis, mock_get_country
    ):
        mock_get_country.side_effect = LookupError(
            "Country not found for lat 24.8 and long 67.0"
        )

        with self.assertRaises(LookupError) as context:
            self.client.get("/fuel-price/24.8/67.0")

        self.assertEqual(
            str(context.exception), "Country not found for lat 24.8 and long 67.0"
        )
        mock_get_country.assert_called_once_with(24.8, 67.0)
        mock_data_in_redis.assert_not_called()

    @mock.patch("src.fuel_service.main.get_country_name_from_patient_location")
    @mock.patch("src.fuel_service.main.data_in_redis")
    def test_sending_fuel_prices_back_to_main_service_with_exception_get_in_redis(
        self, mock_data_in_redis, mock_get_country
    ):
        mock_get_country.return_value = "Pakistan"
        mock_data_in_redis.side_effect = ValueError("Error in data_in_redis")

        with self.assertRaises(ValueError) as context:
            self.client.get("/fuel-price/24.8/67.0")

        self.assertEqual(str(context.exception), "Error in data_in_redis")
        mock_get_country.assert_called_once_with(24.8, 67.0)
        mock_data_in_redis.assert_called_once_with(mock.ANY, "Pakistan")

    @mock.patch("src.fuel_service.main.get_country_name_from_patient_location")
    @mock.patch("src.fuel_service.main.data_in_redis")
    def test_sending_fuel_prices_back_to_main_service_with_exception_nan_NA(
        self, mock_data_in_redis, mock_get_country
    ):
        mock_get_country.return_value = "Pakistan"
        mock_data_in_redis.return_value = None, "N/A"

        response = self.client.get("/fuel-price/24.8/67.0")

        mock_get_country.assert_called_once_with(24.8, 67.0)
        mock_data_in_redis.assert_called_once_with(mock.ANY, "Pakistan")

        self.assertEqual(response.status_code, 200)
        expected_response = {"fuel_price": None, "currency": "N/A"}
        self.assertEqual(response.json(), expected_response)
