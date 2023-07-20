import json
import unittest
from unittest import TestCase
from unittest.mock import patch

import requests  # type: ignore
from fastapi.testclient import TestClient

from src.online_vs_inperson_comparison_service import config, main

client = TestClient(main.app)


def my_get_200(url):
    response = requests.Response()
    response.status_code = 200
    return_json = {}
    patient_lat = 24.853933630083414
    patient_long = 67.01242544738403
    if str.startswith(url, f"{config.PATIENT_URL}"):
        return_json = {"user_id": 1}
    elif str.startswith(url, f"{config.COUNCILLOR_URL}"):
        return_json = {"user_id": 2}
    elif str.startswith(url, f"{config.ACCOUNT_URL}"):
        return_json = {
            "address": {
                "location": {
                    "lat": 1.0,
                    "lng": 2.0,
                },
                "region": "test_region",
            },
        }
    elif str.startswith(url, "https://api.tomtom.com"):
        return_json = {
            "routes": [
                {
                    "summary": {
                        "lengthInMeters": 1.0,
                        "travelTimeInSeconds": 2.0,
                    },
                },
            ],
        }
    elif str.startswith(url, f"{config.PRICES_URL}{patient_lat}/{patient_long}"):
        return_json = {"fuel_price": 262.0, "currency": "test_currency"}

    response._content = json.dumps(return_json).encode("utf-8")
    return response


def my_get_404(unused_url):
    response = requests.Response()
    response.status_code = 404
    return response


@patch("requests.get")
class TestGetData(TestCase):
    def test_api_all_requests_successful(self, mock_request_get):
        mock_request_get.side_effect = my_get_200
        patient_id = "1"
        councillor_id = "2"
        response = client.get(f"/{patient_id}/{councillor_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_time_saved_in_mins": 0.033,
                "total_cost_saved": 0.04030769230769231,
                "currency": "test_currency",
                "co2_saved": 0.12933333333333333,
                "methane_saved": 1.5384615384615385e-07,
            },
        )

    def test_api_all_requests_return_404(self, mock_request_get):
        mock_request_get.side_effect = my_get_404
        patient_id = "1"
        councillor_id = "2"
        with self.assertRaises(requests.exceptions.HTTPError) as context:
            client.get(f"/{patient_id}/{councillor_id}")
        self.assertIn(
            "404 Client Error",
            str(context.exception),
        )

    def test_api_wrong_endpoint(self, mock_request_get):
        response = client.get("/wrong_endpoint")
        self.assertEqual(response.status_code, 404)


class TestApiWorking(unittest.TestCase):
    def test_api_working_200(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            "Api is working, Please give the patient_id and councilor_id after /",
        )

    def test_api_working_404(self):
        response = client.get("/invalid-url")
        self.assertEqual(response.status_code, 404)
