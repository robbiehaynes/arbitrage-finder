# Copyright (c) 2023, Robert Haynes
# All rights reserved.

# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. 

def run_arb_math(market: dict, market_name: str) -> dict:
    
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
        
def run_arb_math_laybet(markets: dict, market_name: str) -> list:
    odds = {'back':{'home': 0.0, 'away': 0.0, 'draw': 0.0}, 'lay':{'home': 0.0, 'away': 0.0, 'draw': 0.0}}
    stakes = {'back':{'home': 0.0, 'away': 0.0, 'draw': 0.0}, 'lay':{'home': 0.0, 'away': 0.0, 'draw': 0.0}}

    results = []

    if market_name == 'h2h_lay':
        for market in markets:
            if market == 'h2h':
                odds['back']['home'] = markets[market]['homeBest'][0]
                odds['back']['away'] = markets[market]['awayBest'][0]
                if 'drawBest' in markets[market]:
                    odds['back']['draw'] = markets[market]['drawBest'][0]
            elif market == 'h2h_lay':
                odds['lay']['home'] = markets[market]['homeBest'][0]
                odds['lay']['away'] = markets[market]['awayBest'][0]
                if 'drawBest' in markets[market]:
                    odds['lay']['draw'] = markets[market]['drawBest'][0]

        if odds['back']['home'] != 0.0 and odds['lay']['home'] < odds['back']['home'] and (1/(odds['back']['home'])) * 100 + (1/(odds['lay']['home'])) * 100 < 97:
            stakes['back']['home'] = 100.0
            stakes['lay']['home'] = (odds['back']['home'] * stakes['back']['home']) / (odds['lay']['home'] - 0.05)
            profit = (odds['back']['home']-1) * stakes['back']['home'] - (odds['lay']['home']-1)*stakes['lay']['home']
            if profit > 0:
                results.append({'type':'home', 'profit':profit, 'odds':[odds['back']['home'],odds['lay']['home']], 'stakes':[100.0, stakes['lay']['home']]})

        if odds['back']['away'] != 0.0 and odds['lay']['away'] < odds['back']['away'] and (1/(odds['back']['away'])) * 100 + (1/(odds['lay']['away'])) * 100 < 97:
            stakes['back']['away'] = 100.0
            stakes['lay']['away'] = (odds['back']['away'] * stakes['back']['away']) / (odds['lay']['away'] - 0.05)
            profit = (odds['back']['away']-1) * stakes['back']['away'] - (odds['lay']['away']-1)*stakes['lay']['away']
            if profit > 0:
                results.append({'type':'away', 'profit':profit, 'odds':[odds['back']['away'],odds['lay']['away']], 'stakes':[100.0, stakes['lay']['away']]})

        if odds['back']['draw'] != 0.0 and odds['lay']['draw'] < odds['back']['draw'] and (1/(odds['back']['draw'])) * 100 + (1/(odds['lay']['draw'])) * 100 < 97:
            stakes['back']['draw'] = 100.0
            stakes['lay']['draw'] = (odds['back']['draw'] * stakes['back']['draw']) / (odds['lay']['draw'] - 0.05)
            profit = (odds['back']['draw']-1) * stakes['back']['draw'] - (odds['lay']['draw']-1)*stakes['lay']['draw']
            if profit > 0:
                results.append({'type':'draw', 'profit':profit, 'odds':[odds['back']['draw'],odds['lay']['draw']], 'stakes':[100.0, stakes['lay']['draw']]})

    return results if len(results) > 0 else None

def find_arbitrage(database: dict) -> list :

    results = []

    for sport in database:
        for match in database[sport]:
            home_team = database[sport][match]['home_team']
            away_team = database[sport][match]['away_team']
            for market in database[sport][match]['markets']:
                if market == 'h2h':
                    calculations = run_arb_math(database[sport][match]['markets'][market], market)
                    if calculations != None:
                        result = {
                            'sport': sport,
                            'type': 'h2h',
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
                    calculations = run_arb_math(database[sport][match]['markets'][market], market)
                    if calculations != None:
                        result = {
                            'sport': sport,
                            'type': 'totals',
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

                elif market == 'h2h_lay':
                    calculations = run_arb_math_laybet(database[sport][match]['markets'], market)
                    if calculations != None:

                        result = {
                            'sport': sport,
                            'type': 'laybet',
                            'home_team': home_team,
                            'away_team': away_team
                        }

                        for calculation in calculations:
                            if calculation['type'] == 'home':
                                result['home_stake'] = {
                                    'profit': calculation['profit'],
                                    'back_bookmaker': database[sport][match]['markets']['h2h']['homeBest'][1],
                                    'lay_bookmaker': database[sport][match]['markets'][market]['homeBest'][1],
                                    'back_price': calculation['odds'][0],
                                    'lay_price': calculation['odds'][1],
                                    'lay_stake': calculation['stakes'][1]
                                }

                            elif calculation['type'] == 'away':
                                result['away_stake'] = {
                                    'profit': calculation['profit'],
                                    'back_bookmaker': database[sport][match]['markets']['h2h']['awayBest'][1],
                                    'lay_bookmaker': database[sport][match]['markets'][market]['awayBest'][1],
                                    'back_price': calculation['odds'][0],
                                    'lay_price': calculation['odds'][1],
                                    'lay_stake': calculation['stakes'][1]
                                }

                            elif calculation['type'] == 'draw':
                                result['draw_stake'] = {
                                    'profit': calculation['profit'],
                                    'back_bookmaker': database[sport][match]['markets']['h2h']['drawBest'][1],
                                    'lay_bookmaker': database[sport][match]['markets'][market]['drawBest'][1],
                                    'back_price': calculation['odds'][0],
                                    'lay_price': calculation['odds'][1],
                                    'lay_stake': calculation['stakes'][1]
                                }

                        results.append(result)

    return results