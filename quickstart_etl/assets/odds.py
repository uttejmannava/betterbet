import requests
import json
import os
from datetime import datetime
import warnings

from .constants import *
from dagster import AssetExecutionContext, MaterializeResult, MetadataValue, EnvVar, asset, ExperimentalWarning
from ..resources import *


# Suppressing ExperimentalWarning
warnings.filterwarnings("ignore", category=ExperimentalWarning)


@asset
def raw_odds_data(odds_api: OddsAPIResource) -> list:
    """
    Pull raw betting odds from specified markets and bookmakers.
    API Docs: https://the-odds-api.com/liveapi/guides/v4/index.html
    """
    
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

    # each sport requires a separate API call
    all_odds_data = []

    for sport in SPORT:
        odds_response = odds_api.request(sport, params)
        if odds_response.status_code != 200:
            print(odds_response.text)
            # raise Exception(f"API request failed: {odds_response.text}")
        else:
            all_odds_data.extend(odds_response.json())

    return all_odds_data

    # for n in SPORT:
    #     odds_response = odds_api.request(n, params)

    #     # Handle response error codes
    #     if odds_response.status_code != 200:
    #         print(odds_response.text)
    #     else:
    #         raw_odds_json = odds_response.json()
    #         timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    #         filename = f"data/raw_odds_{n}_{timestamp}.json"
    #         with open(filename, "w") as f:
    #             json.dump(raw_odds_json, f)
    #         filename_list.append(filename)
    
    # return filename_list


@asset()
def processed_odds_data(raw_odds_data: list[dict]) -> dict:
    """
    Loads all games into a Python dictionary.
    Receives JSON in-memory (Pythonic object).
    """
    print("raw_odds_data:", raw_odds_data)
    processed_data = {}
    
    # Process each sport's games separately
    for game in raw_odds_data:
        print("Processing game:", game['id'])  # Debug print statement
        game_id = game['id']
        processed_data[game_id] = {
            'sport_key': game['sport_key'],
            'sport_title': game['sport_title'],
            'commence_time': game['commence_time'],
            'home_team': game['home_team'],
            'away_team': game['away_team'],
            'bookmakers': {}
        }

        for bookmaker in game['bookmakers']:
            bm_key = bookmaker['key']
            processed_data[game_id]['bookmakers'][bm_key] = {
                'title': bookmaker['title'],
                'last_update': bookmaker['last_update'],
                'markets': {}
            }

            for market in bookmaker['markets']:
                market_key = market['key']
                processed_data[game_id]['bookmakers'][bm_key]['markets'][market_key] = {
                    'last_update': market['last_update'],
                    'outcomes': {
                        outcome['name']: {
                            'price': outcome['price'],
                            'point': outcome.get('point')
                        } for outcome in market['outcomes']
                    }
                }
    print("PROCESSED DATA:", processed_data)
    return processed_data


@asset()
def arbitrage_pairs(processed_odds_data: dict) -> dict:
    arbitrage_opportunities = {}

    for game_id, game_data in processed_odds_data.items():
        arbitrage_opportunities[game_id] = {
            'sport_key': game_data['sport_key'],
            'sport_title': game_data['sport_title'],
            'home_team': game_data['home_team'],
            'away_team': game_data['away_team'],
            'commence_time': game_data['commence_time'],
            'arbitrage_opportunities': []
        }

        for market_key in MARKETS:
            best_odds = {'team1': {'odds': -1000000, 'bookmaker': ''}, 
                         'team2': {'odds': -1000000, 'bookmaker': ''}}

            for bookmaker, bm_data in game_data['bookmakers'].items():
                if market_key in bm_data['markets']:
                    outcomes = bm_data['markets'][market_key]['outcomes']

                    if market_key == 'h2h' or market_key == 'spreads':
                        team1, team2 = game_data['home_team'], game_data['away_team']
                    elif market_key == 'totals':
                        team1, team2 = 'Over', 'Under'

    
    return arbitrage_opportunities
    
    pass


@asset()
def low_hold_pairs(processed_odds_data: dict) -> dict:
    pass


@asset()
def positive_ev_pairs(processed_odds_data: dict) -> dict:
    pass