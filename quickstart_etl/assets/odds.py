import requests
import json
import os

from . import constants
from dagster import AssetExecutionContext, MaterializeResult, MetadataValue, EnvVar, asset
from ..resources import *

@asset
def raw_odds_data(odds_api: OddsAPIResource) -> None:
    """
    Pull raw betting odds from specified markets and bookmakers.
    API Docs: https://the-odds-api.com/liveapi/guides/v4/index.html
    """

    # Defining params for request
    SPORT = 'baseball_mlb' # use the sport_key from the /sports endpoint, or use 'upcoming' to see the next 8 games across all sports
    REGIONS = ['us'] # uk | us | eu | au. Multiple can be specified if comma delimited
    BOOKMAKERS = ['betmgm', 'betrivers', 'draftkings', 'fanduel', 'ballybet', 'espnbet', 'pinnacle', 'betway'] # Every group of 10 bookmakers is the equivalent of 1 region.
    MARKETS = ['h2h', 'spreads', 'totals'] # h2h | spreads | totals. Multiple can be specified if comma delimited
    ODDS_FORMAT = 'american' # decimal | american
    DATE_FORMAT = 'iso' # iso | unix
    
    '''
    The usage quota cost = [number of markets specified] x [number of regions specified]
    For examples of usage quota costs, see https://the-odds-api.com/liveapi/guides/v4/#usage-quota-costs
    '''

    # Grab JSON odds data
    params={
            'api_key': os.getenv("THE_ODDS_API_KEY"),
            # 'regions': REGIONS,
            'bookmakers': ','.join(BOOKMAKERS),
            'markets': ','.join(MARKETS),
            'oddsFormat': ODDS_FORMAT,
            'dateFormat': DATE_FORMAT,
        }

    odds_response = odds_api.request(SPORT, params)

    # Handle response error codes
    if odds_response.status_code != 200:
        print(odds_response.text)
    else:
        raw_odds_json = odds_response.json()
        with open("data/raw_odds.json", "w") as f:
            json.dump(raw_odds_json, f)
