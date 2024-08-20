
def calculate_implied_probability(american_odds: int) -> float:
    if american_odds > 0:
        return 100 / (american_odds + 100)
    else:
        return -american_odds / (-american_odds + 100)

def calculate_arbitrage(prob1: float, prob2: float) -> float:
    return (1 / prob1) + (1 / prob2)