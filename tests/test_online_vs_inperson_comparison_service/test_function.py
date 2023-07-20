import json
import unittest
from unittest import TestCase
from unittest.mock import patch

import requests  # type: ignore

from src.online_vs_inperson_comparison_service import functions


class TestGetLocationData(unittest.TestCase):
    @patch("src.online_vs_inperson_comparison_service.functions.get_data_from_url")
    def test_get_location_data_patient(self, mock_get_data_from_url):
        # Mock the get_data_from_url function
        mock_get_data_from_url.return_value = {
            "user_id": 1,
            "address": {"location": {"lat": 1.0, "lng": 2.0}, "region": "test_region"},
        }

        # Call the get_location_data function for a patient
        result = functions.get_location_data(1, True)

        # Assert the result matches the expected values
        expected_result = {"latitude": 1.0, "longitude": 2.0, "region": "test_region"}
        self.assertEqual(result, expected_result)

    @patch("src.online_vs_inperson_comparison_service.functions.get_data_from_url")
    def test_get_location_data_councillor(self, mock_get_data_from_url):
        # Mock the get_data_from_url function
        mock_get_data_from_url.return_value = {
            "user_id": 2,
            "address": {"location": {"lat": 3.0, "lng": 4.0}, "region": "test_region"},
        }

        # Call the get_location_data function for a councillor
        result = functions.get_location_data(2, False)

        # Assert the result matches the expected values
        expected_result = {"latitude": 3.0, "longitude": 4.0, "region": "test_region"}
        self.assertEqual(result, expected_result)


@patch("src.online_vs_inperson_comparison_service.functions.requests.get")
class TestGetDataFromUrl(TestCase):
    def test_get_data_200_response(self, mock_request_get):
        return_json = {"test_key": "test_value"}
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps(return_json).encode("utf-8")
        mock_request_get.return_value = response
        url = "http://example.com/api/data"
        response_data = functions.get_data_from_url(url)

        mock_request_get.assert_called_once_with(url)
        self.assertEqual(response_data, return_json)

    def test_get_data_404_response(self, mock_request_get):
        response = requests.Response()
        response.status_code = 404
        mock_request_get.return_value = response
        url = "http://example.com/api/data"
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            functions.get_data_from_url(url)

        mock_request_get.assert_called_once_with(url)

        self.assertIn(
            "404 Client Error",
            str(context.exception),
        )


class TestGetDistanceTimeFromTomtom(TestCase):
    @patch("src.online_vs_inperson_comparison_service.functions.get_data_from_url")
    def test_get_distance_time_from_tomtom(self, mock_get_data_from_url):
        # Mock the response data
        route_data = {
            "routes": [
                {"summary": {"lengthInMeters": 5000, "travelTimeInSeconds": 1200}}
            ]
        }
        mock_get_data_from_url.return_value = route_data

        # Define dummy coordinates
        dummy_patient_lat = 12.34
        dummy_patient_long = 56.78
        dummy_councillor_lat = 90.12
        dummy_councillor_long = 34.56

        # Call the function
        result = functions.get_distance_time_from_tomtom(
            dummy_patient_lat,
            dummy_patient_long,
            dummy_councillor_lat,
            dummy_councillor_long,
        )

        expected_result = {"distance": 5.0, "time": 20.0}

        self.assertDictEqual(result, expected_result)


class TestCalculateSavings(unittest.TestCase):
    @patch("src.online_vs_inperson_comparison_service.functions.estimate_co2")
    def test_calculate_savings(self, mock_estimate_co2):
        fuel_price = 1.5
        distance = 100
        mock_estimate_co2.return_value = distance
        methane_emission_factor = 0.001

        avg_fuel_consumption = 5.0

        result = functions.calculate_savings(distance, fuel_price, avg_fuel_consumption)

        self.assertListEqual(
            [result["total_cost"], result["co2_saved"], result["methane_saved"]],
            [
                (distance / avg_fuel_consumption) * fuel_price,
                100,
                (distance / avg_fuel_consumption) * methane_emission_factor,
            ],
        )


if __name__ == "__main__":
    unittest.main()
