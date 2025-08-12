import requests
from abc import ABC, abstractmethod
import logging

class UnauthorizedAccessException(Exception):
    """Custom exception for unauthorized access (401)."""
    pass
class AbstractHttpClient(ABC):
    """
    Abstract class to send HTTP GET and POST requests.
    """

    @abstractmethod
    def send_get_request(self, url: str, headers: dict = None, params: dict = None) -> requests.Response:
        """
        Send an HTTP GET request to a specified URL.

        :param url: The endpoint URL for the GET request.
        :param headers: Optional headers for the GET request.
        :param params: Optional query parameters for the GET request.
        :return: Response object from the GET request.
        """
        pass

    @abstractmethod
    def send_post_request(self, url: str, headers: dict = None, data: dict = None, json: dict = None) -> requests.Response:
        """
        Send an HTTP POST request to a specified URL.

        :param url: The endpoint URL for the POST request.
        :param headers: Optional headers for the POST request.
        :param data: Form data to be sent in the POST request body.
        :param json: JSON data to be sent in the POST request body.
        :return: Response object from the POST request.
        """
        pass


class HttpClient(AbstractHttpClient):
    """
    Concrete implementation of the AbstractHttpClient class.
    """

    def send_get_request(self, url: str, headers: dict = None, params: dict = None) -> requests.Response:
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 401:
                raise UnauthorizedAccessException('Unauthorized access: Invalid or missing token.')
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx/5xx)
            return response

        except requests.RequestException as e:
            logging.error(f"GET request failed: {e}")
            raise

    def send_post_request(self, url: str, headers: dict = None, data: dict = None, json: dict = None) -> requests.Response:
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx/5xx)
            return response
        except requests.RequestException as e:
            logging.error(f"POST request failed: {e}")
            raise

