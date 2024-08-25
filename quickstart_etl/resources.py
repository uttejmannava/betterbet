import requests
from requests import Response

from dagster import Definitions, ConfigurableResource, EnvVar

class OddsBlazeAPIResource(ConfigurableResource):

    def request(self, params_dict: dict) -> Response:

        return requests.get(
            f'https://api.oddsblaze.com/v1/odds/',
            params=params_dict,
            # headers={"user-agent": "dagster"},
        )