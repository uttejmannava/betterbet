# store file paths, date formats, dates, etc. as constants

# Defining params for request
SPORTSBOOKS =  [
    '888sport_ontario',
    'betrivers_ontario',
    'betsafe_ontario',
    'bodog',
    'bally_bet',
    'casumo_ontario', 
    'draftkings_ontario',
    'fanduel_ontario',
    'northstar_bets_ontario',
    'pointsbet_ontario',
    'pinnacle',
    'thescore_bet_ontario'
    ]

LEAGUE_MARKETS = {
    'mlb': 
        [
            # moneylines
            '1st_3_innings_moneyline',
            '1st_5_innings_moneyline',
            # '1st_inning_moneyline',
            'moneyline',

            # #run lines
            # 'run_line',
        ],

    # 'united_states_major_league_soccer': 
    #     [
    #         'total_corners',
    #         ''           
    #     ],
    
    'nfl': 
        [
            '1st_half_moneyline',
            'moneyline',
        ],
    
    # 'england_premier_league':
    #     [
    #         'total_corners',
    #         'total_shots',
    #         'total_shots_on_target',
    #         'total_red_cards',

    #     ]
    
}

PRICE = 'american' # decimal | american