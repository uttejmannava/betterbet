import requests
import json
import os
from datetime import datetime, timedelta
import pytz
import warnings

from .constants import *
from dagster import (
    AssetExecutionContext, 
    MaterializeResult,
    MetadataValue,
    EnvVar,
    asset,
    ExperimentalWarning,
)
from ..resources import *
from .functions import *


# Suppressing ExperimentalWarning
warnings.filterwarnings("ignore", category=ExperimentalWarning)


@asset
def raw_odds_data(odds_api: OddsBlazeAPIResource) -> list:
    """
    Pull raw betting odds from specified markets and bookmakers.
    OddsBlaze API Docs: https://docs.oddsblaze.com/api/odds
    """

    # each league requires a separate API call
    all_odds_data = []

    for league in LEAGUE_MARKETS:

        params={
            'key': os.getenv("ODDSBLAZE_KEY"),
            'league': league,
            'market': ','.join(LEAGUE_MARKETS[league]),
            'price': PRICE,
            'main': 'true',
            # 'main_id': 'true'
        }
        print(params)

        odds_response = odds_api.request(params)

        if odds_response.status_code != 200:
            print(odds_response.text)
            # raise Exception(f"API request failed: {odds_response.text}")
        else:
            all_odds_data.extend(odds_response.json()["games"]) # revisit and see how to add multiple leagues

    filename = f"data/raw_odds_test.json"
    with open(filename, "w") as f:
        json.dump(all_odds_data, f)

    # Return a Pythonic object to avoid I/O
    return all_odds_data


@asset()
def processed_games(raw_odds_data: list[dict]) -> list:
    """
    Loads all games into a Python dictionary.
    Receives JSON in-memory (Pythonic object).
    """
    processed_games = raw_odds_data

    for game in processed_games:
        print(game['id'])

        game['start'] = datetime.strptime(game['start'], "%Y-%m-%dT%H:%M:%S")
        game['start'] = pytz.UTC.localize(game['start'])

        game['sportsbooks'] = [
            sportsbook for sportsbook in game['sportsbooks']
            if sportsbook['id'] in SPORTSBOOKS
        ]

    current_time = datetime.utcnow().replace(tzinfo=pytz.UTC)

    processed_games = [
        game for game in processed_games
        if ( not (current_time - game['start']).total_seconds() / 60 > 30 and not game['live'] )
    ]

    print("length processed:", len(processed_games))
    return processed_games


@asset()
def best_odds_pairs(processed_games: list) -> dict:
    """
    For each game and market, identifies the best odds for every pair.
    There can be a max of one best odds pair for each market, for each game.
    If a game has no best odds pairs, it is not returned in the final dictionary.
    arb_pairs and low_odds_pairs lists track which, if any, best odds pairs fall under those respective categories.
    """
    best_odds_pairs = {}

    for game in processed_games:

        league_key = game['id'].split(':')[0]

        best_odds_pairs[game['id']] = {
            'sport': game['sport'],
            'league_key': league_key,
            'league_name': game['league'],
            'home_team': game['teams']['home'],
            'away_team': game['teams']['away'],
            'start_time': str(game['start']),
            'status': game['status'],
            'is_live': game['live'],
            'pairs': [],
            'arb_pairs': [],
            'low_hold_pairs': []
        }

        for market in LEAGUE_MARKETS[league_key]:

            home_team_id = game['teams']['home']['id'].split(':')[1]
            away_team_id = game['teams']['away']['id'].split(':')[1]

            best_odds = {home_team_id: {'odds': -1000000, 'bookmaker': ''},
                         away_team_id: {'odds': -1000000, 'bookmaker': ''}}
            
            for sportsbook in game['sportsbooks']:
                
                for bet in sportsbook['odds']:

                    bet_market = bet['id'].split(':')[1]
                    bet_winning_team = bet['id'].split(':')[2]

                    if market == bet_market:
                        if int(bet['price']) > best_odds[bet_winning_team]['odds']:
                            best_odds[bet_winning_team]['odds'] = int(bet['price'])
                            best_odds[bet_winning_team]['bookmaker'] = sportsbook['id']

            if best_odds[home_team_id]['bookmaker'] == '' and best_odds[away_team_id]['bookmaker'] == '':
                continue
            
            print("market:", market, " | best odds:", best_odds)

            home_prob = round(calculate_implied_probability(best_odds[home_team_id]['odds']), 2)
            away_prob = round(calculate_implied_probability(best_odds[away_team_id]['odds']), 2)

            arb_value = round(calculate_arbitrage(home_prob, away_prob), 2)
            profit_percentage = str(round((1 - arb_value) * 100, 2))

            best_odds_pairs[game['id']]['pairs'].append({ # Every market has a best odds pair
                'market': market,
                'home_team': {
                    'best_odds': best_odds[home_team_id]['odds'],
                    'bookmaker': best_odds[home_team_id]['bookmaker'],
                    'implied_probability': home_prob
                },
                'away_team': {
                    'best_odds': best_odds[away_team_id]['odds'],
                    'bookmaker': best_odds[away_team_id]['bookmaker'],
                    'implied_probability': away_prob
                },
                'arb_value': arb_value,
                'profit_percentage': profit_percentage
            })

            if arb_value < 1: # This indicates an arbitrage opportunity

                best_odds_pairs[game['id']]['arb_pairs'].append({
                    'market': market,
                    'home_team': {
                        'best_odds': best_odds[home_team_id]['odds'],
                        'bookmaker': best_odds[home_team_id]['bookmaker'],
                        'implied_probability': home_prob
                    },
                    'away_team': {
                        'best_odds': best_odds[away_team_id]['odds'],
                        'bookmaker': best_odds[away_team_id]['bookmaker'],
                        'implied_probability': away_prob
                    },
                    'arb_value': arb_value,
                    'profit_percentage': profit_percentage
                })

            elif arb_value == 1: # This indicates a low hold opportunity

                best_odds_pairs[game['id']]['low_hold_pairs'].append({
                    'market': market,
                    'home_team': {
                        'best_odds': best_odds[home_team_id]['odds'],
                        'bookmaker': best_odds[home_team_id]['bookmaker'],
                        'implied_probability': home_prob
                    },
                    'away_team': {
                        'best_odds': best_odds[away_team_id]['odds'],
                        'bookmaker': best_odds[away_team_id]['bookmaker'],
                        'implied_probability': away_prob
                    },
                    'arb_value': arb_value,
                    'profit_percentage': profit_percentage
                })

    # best_odds_pairs = {k: v for k, v in best_odds_pairs.items() if v['arb_pairs']}
    
    filename = f"data/best_odds_pairs.json" 
    with open(filename, "w") as f:
        json.dump(best_odds_pairs, f)

    return best_odds_pairs


# # @asset()
# # def positive_ev_pairs(processed_games: list) -> None:
# #     pass