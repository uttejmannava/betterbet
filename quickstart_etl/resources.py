import requests
from requests import Response

from dagster import Definitions, ConfigurableResource, EnvVar

class OddsAPIResource(ConfigurableResource):

    def request(self, sport_key: str, params_dict: dict) -> Response:
        # return requests.get(
        #     f"https://my-api.com/{endpoint}",
        #     headers={"user-agent": "dagster"},
        # )
        return requests.get(
            f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds',
            params=params_dict
        )
    
        # return requests.get(
        #     f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
        #     params={
        #         'api_key': context.resources.odds_api_key,
        #         # 'regions': REGIONS,
        #         'bookmakers': ','.join(BOOKMAKERS),
        #         'markets': ','.join(MARKETS),
        #         'oddsFormat': ODDS_FORMAT,
        #         'dateFormat': DATE_FORMAT,
        #     }
        # )