import math
import unittest
from unittest import TestCase, mock

from redis import Redis

from src.fuel_service.functions import (
    data_in_redis,
    get_country_name_from_patient_location,
    scrapping_from_url,
)


class TestGetCountryName(TestCase):
    @mock.patch("src.fuel_service.functions.Nominatim")
    def test_get_country_name_from_patient_location(self, mock_nominatim):
        # Mocking the reverse method of Nominatim
        mock_location = mock_nominatim().reverse.return_value
        mock_location.raw = {"address": {"country": "United States"}}

        # Provide sample latitude and longitude values for testing
        lat = 37.7749
        long = -122.4194

        # Call the function and assert the result
        country_name = get_country_name_from_patient_location(lat, long)
        self.assertEqual(country_name, "United-States")

    @mock.patch("src.fuel_service.functions.Nominatim")
    def test_get_country_name_from_patient_location_with_exception(
        self, mock_nominatim
    ):
        # Mocking the reverse method of Nominatim to return None
        mock_nominatim().reverse.return_value = None
        print(mock_nominatim)
        # Provide sample latitude and longitude values for testing
        lat = 37.7749
        long = -122.4194

        # Call the function and assert that it raises a LookupError
        with self.assertRaises(LookupError) as context:
            get_country_name_from_patient_location(lat, long)
        print(str(context.exception))
        # Assert the error message contains the expected lat and long values
        self.assertIn(str(lat), str(context.exception))
        self.assertIn(str(long), str(context.exception))


class TestScrapingFromUlr(TestCase):
    @mock.patch("src.fuel_service.functions.requests.get")
    def test_scrapping_from_url(self, mock_get):
        # Mocking the response from the requests library

        mock_get.status_code = 200
        mock_get.content = """
          <div id="graphPageLeft">
            <table>
                <tbody>
                    <tr>
                        <th height="30">&nbsp;PKR</th>
                        <td height="30" align="center">262.000</td>
                        <td height="30" align="center">991.777</td>
                    </tr>
                    <tr bgcolor="#f8f8f8">
                        <th height="30">&nbsp;USD</th>
                        <td height="30" align="center">0.914</td>
                        <td height="30" align="center">3.460</td>
                    </tr>
                    <tr>
                        <th height="30" style="border-bottom: 1px solid #f8f8f8">&nbsp;EUR</th>
                        <td height="30" style="border-bottom: 1px solid #f8f8f8" align="center">0.838</td>
                        <td height="30" style="border-bottom: 1px solid #f8f8f8" align="center">3.172</td>
                    </tr>
                </tbody>
            </table>
          </div>

        """
        mock_get.return_value = mock_get

        # Mocking the redis client
        # Mocking the Redis client
        redis_client_mock = mock.Mock(spec=Redis)

        country = "USA"

        # Calling the function
        result = scrapping_from_url(redis_client_mock, country)

        # Asserting the expected result
        expected_result = (0.914, "USD")
        assert result == expected_result

        # Asserting the Redis calls
        expected_key = "USA"
        expected_value = "0.914:USD"
        redis_client_mock.set.assert_called_once_with(expected_key, expected_value)
        redis_client_mock.expire.assert_called_once_with(expected_key, 86400)


class TestDataInRedis(TestCase):
    @mock.patch("src.fuel_service.functions.scrapping_from_url")
    def test_data_in_redis_if_country_exists(self, mock_scrapping_from_url):
        redis_client_mock = mock.Mock(spec=Redis)

        country = "USA"
        redis_data = "2.345:USD"
        redis_client_mock.exists.return_value = True
        redis_client_mock.get.return_value = redis_data.encode()
        result = data_in_redis(redis_client_mock, country)
        expected_result = (2.345, "USD")
        assert result == expected_result

        redis_client_mock.exists.assert_called_once_with(country)
        redis_client_mock.get.assert_called_once_with(country)
        mock_scrapping_from_url.assert_not_called()

    @mock.patch("src.fuel_service.functions.scrapping_from_url")
    def test_data_in_redis_if_country_not_exists(self, mock_scrapping_from_url):
        redis_client_mock = mock.Mock(spec=Redis)

        country = "UK"
        fuel_price = 1.234
        currency = "GBP"
        mock_scrapping_from_url.return_value = (fuel_price, currency)
        redis_client_mock.exists.return_value = False

        result = data_in_redis(redis_client_mock, country)

        expected_result = (1.234, "GBP")
        assert result == expected_result

        redis_client_mock.exists.assert_called_once_with(country)
        redis_client_mock.get.assert_not_called()
        mock_scrapping_from_url.assert_called_once_with(redis_client_mock, country)

        redis_client_mock.reset_mock()
        mock_scrapping_from_url.reset_mock()

    @mock.patch("src.fuel_service.functions.scrapping_from_url")
    def test_data_in_redis_if_country_is_none(self, mock_scrapping_from_url):
        redis_client_mock = mock.Mock(spec=Redis)

        country = None
        redis_client_mock.exists.return_value = False

        result = data_in_redis(redis_client_mock, country)

        expected_result = (float("nan"), "N/A")
        assert math.isnan(result[0]) and result[1] == expected_result[1]

        redis_client_mock.exists.assert_not_called()
        redis_client_mock.get.assert_not_called()
        mock_scrapping_from_url.assert_not_called()


if __name__ == "__main__":
    unittest.main()
