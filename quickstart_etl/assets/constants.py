# store file paths, api endpoints, date formats, dates, etc. as constants

# Defining params for request
SPORT = ['baseball_mlb'] # use the sport_key from the /sports endpoint, or use 'upcoming' to see the next 8 games across all sports
REGIONS = ['us'] # uk | us | eu | au. Multiple can be specified if comma delimited
BOOKMAKERS = ['betmgm', 'betrivers', 'draftkings', 'fanduel', 'ballybet', 'espnbet', 'pinnacle', 'betway'] # Every group of 10 bookmakers is the equivalent of 1 region.
MARKETS = ['h2h', 'spreads', 'totals'] # h2h | spreads | totals. Multiple can be specified if comma delimited
ODDS_FORMAT = 'american' # decimal | american
DATE_FORMAT = 'iso' # iso | unix