def run_arbitrage_math(market: dict, market_name: str) -> dict:
    
    if market_name == 'h2h':
        home_price = market['homeBest'][0]
        away_price = market['awayBest'][0]
        draw_price = market['drawBest'][0] if 'drawBest' in market else 0

        home_implied = (1/home_price) * 100
        away_implied = (1/away_price) * 100
        draw_implied = (1/draw_price) * 100 if draw_price != 0 else 0

        if draw_implied != 0:
            combined_margin = home_implied + away_implied + draw_implied
            if (combined_margin) < 100:
                return {'home_stake': (100*home_implied)/combined_margin, 'away_stake': (100*away_implied)/combined_margin, 'draw_stake': (100*draw_implied)/combined_margin, 'roi': 100-combined_margin}
            else:
                return None
        else:
            combined_margin = home_implied + away_implied
            if (combined_margin) < 100:
                return {'home_stake': (100*home_implied)/combined_margin, 'away_stake': (100*away_implied)/combined_margin, 'roi': 100-combined_margin}
            else:
                return None
    
    elif market_name == 'totals':
        over_price = market['overBest'][0]
        under_price = market['underBest'][0]

        if over_price == 0 or under_price == 0:
            return None

        over_implied = (1/over_price) * 100
        under_implied = (1/under_price) * 100

        combined_margin = over_implied + under_implied
        if (combined_margin) < 100:
            return {'over_stake': (100*over_implied)/combined_margin, 'under_stake': (100*under_implied)/combined_margin, 'roi': 100-combined_margin}
        else:
            return None


def find_arbitrage(database: dict) -> list :

    results = []

    for sport in database:
        for match in database[sport]:
            home_team = database[sport][match]['home_team']
            away_team = database[sport][match]['away_team']
            for market in database[sport][match]['markets']:
                if market == 'h2h':
                    calculations = run_arbitrage_math(database[sport][match]['markets'][market], market)
                    if calculations != None:
                        result = {
                            'sport': sport,
                            'home_team': home_team,
                            'away_team': away_team,
                            'roi': calculations['roi'],
                            'home_stake': {
                                'bookmaker': database[sport][match]['markets'][market]['homeBest'][1],
                                'price': database[sport][match]['markets'][market]['homeBest'][0],
                                'stake': calculations['home_stake']
                            },
                            'away_stake': {
                                'bookmaker': database[sport][match]['markets'][market]['awayBest'][1],
                                'price': database[sport][match]['markets'][market]['awayBest'][0],
                                'stake': calculations['away_stake']
                            }
                        }

                        if 'draw_stake' in calculations:
                            result['draw_stake'] = {
                                'bookmaker': database[sport][match]['markets'][market]['drawBest'][1],
                                'price': database[sport][match]['markets'][market]['drawBest'][0],
                                'stake': calculations['draw_stake']
                            }

                        results.append(result)

                elif market == 'totals':
                    calculations = run_arbitrage_math(database[sport][match]['markets'][market], market)
                    if calculations != None:
                        result = {
                            'sport': sport,
                            'home_team': home_team,
                            'away_team': away_team,
                            'roi': calculations['roi'],
                            'over_stake': {
                                'bookmaker': database[sport][match]['markets'][market]['overBest'][1],
                                'price': database[sport][match]['markets'][market]['overBest'][0],
                                'stake': calculations['home_stake']
                            },
                            'under_stake': {
                                'bookmaker': database[sport][match]['markets'][market]['underBest'][1],
                                'price': database[sport][match]['markets'][market]['underBest'][0],
                                'stake': calculations['away_stake']
                            }
                        }

                        results.append(result)

    return results