from colorama import Fore, Style

# Copyright (c) 2023, Robert Haynes
# All rights reserved.

# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. 

class ArbitrageFinder:
    def __init__(self, database) -> None:
        self.database = database

    @staticmethod
    def run_arb_math(market: dict, market_name: str) -> dict:
        
        if market_name == 'h2h':
            # Get the odds into variables for the current match
            home_price = market['homeBest'][0]
            away_price = market['awayBest'][0]
            draw_price = market['drawBest'][0] if 'drawBest' in market else 0

            if home_price == 0 or away_price == 0:
                return None

            # Calculate the implied probability of each outcome
            home_implied = (1/home_price) * 100
            away_implied = (1/away_price) * 100
            draw_implied = (1/draw_price) * 100 if draw_price != 0 else 0

            # # # # # # # # # # # # # # # # # # # # # # # #
            #
            #   If the combined implied probability of the
            #   outcomes is less than 100%, then there is
            #   an arbitrage opportunity.
            #   The stakes are calculated as follows:
            #   stake = (100 * implied probability of outcome) / combined margin
            #
            # # # # # # # # # # # # # # # # # # # # # # # #
            if draw_implied != 0:
                combined_margin = home_implied + away_implied + draw_implied
                if (combined_margin) < 100:
                    print(Fore.GREEN + f'Opportunity found in {market_name} market' + Style.RESET_ALL)
                    return {'home_stake': (100*home_implied)/combined_margin, 'away_stake': (100*away_implied)/combined_margin, 'draw_stake': (100*draw_implied)/combined_margin, 'roi': 100-combined_margin}
                else:
                    return None
            else:
                combined_margin = home_implied + away_implied
                if (combined_margin) < 100:
                    print(Fore.GREEN + f'Opportunity found in {market_name} market' + Style.RESET_ALL)
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
                print(Fore.GREEN + f'Opportunity found in {market_name} market' + Style.RESET_ALL)
                return {'over_stake': (100*over_implied)/combined_margin, 'under_stake': (100*under_implied)/combined_margin, 'roi': 100-combined_margin}
            else:
                return None

    @staticmethod 
    def run_arb_math_laybet(markets: dict, market_name: str) -> list:
        odds = {'back':{'home': 0.0, 'away': 0.0, 'draw': 0.0}, 'lay':{'home': 0.0, 'away': 0.0, 'draw': 0.0}}
        stakes = {'back':{'home': 0.0, 'away': 0.0, 'draw': 0.0}, 'lay':{'home': 0.0, 'away': 0.0, 'draw': 0.0}}

        results = []

        if market_name == 'h2h_lay':
            # Get the best backing and lay odds for each match
            # including the draw if it exists
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

            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            #
            #   If there are backing odds and the lay odds are lower, then calculate
            #   if the implied odds are < 100
            #   If so, the laybet stake is calculated with the following:
            #   (back odds * back stake) / (lay odds - commission)
            #   The profit is then calculated with the following:
            #   (back odds - 1) * back stake - (lay odds - 1) * lay stake
            #   If the profit is > 0, then add the result to the results list
            #
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            if odds['back']['home'] != 0.0 and odds['lay']['home'] != 0.0 and odds['lay']['home'] < odds['back']['home'] and (1/(odds['back']['home'])) * 100 + (1/(odds['lay']['home'])) * 100 < 97:
                stakes['back']['home'] = 100.0
                stakes['lay']['home'] = (odds['back']['home'] * stakes['back']['home']) / (odds['lay']['home'] - 0.05)
                profit = (odds['back']['home']-1) * stakes['back']['home'] - (odds['lay']['home']-1)*stakes['lay']['home']
                if profit > 0:
                    print(Fore.GREEN + f'Opportunity found in {market_name} market' + Style.RESET_ALL)
                    results.append({'type':'home', 'profit':profit, 'odds':[odds['back']['home'],odds['lay']['home']], 'stakes':[100.0, stakes['lay']['home']]})

            if odds['back']['away'] != 0.0 and odds['lay']['away'] != 0.0 and odds['lay']['away'] < odds['back']['away'] and (1/(odds['back']['away'])) * 100 + (1/(odds['lay']['away'])) * 100 < 97:
                stakes['back']['away'] = 100.0
                stakes['lay']['away'] = (odds['back']['away'] * stakes['back']['away']) / (odds['lay']['away'] - 0.05)
                profit = (odds['back']['away']-1) * stakes['back']['away'] - (odds['lay']['away']-1)*stakes['lay']['away']
                if profit > 0:
                    print(Fore.GREEN + f'Opportunity found in {market_name} market' + Style.RESET_ALL)
                    results.append({'type':'away', 'profit':profit, 'odds':[odds['back']['away'],odds['lay']['away']], 'stakes':[100.0, stakes['lay']['away']]})

            if odds['back']['draw'] != 0.0 and odds['lay']['draw'] != 0.0 and odds['lay']['draw'] < odds['back']['draw'] and (1/(odds['back']['draw'])) * 100 + (1/(odds['lay']['draw'])) * 100 < 97:
                stakes['back']['draw'] = 100.0
                stakes['lay']['draw'] = (odds['back']['draw'] * stakes['back']['draw']) / (odds['lay']['draw'] - 0.05)
                profit = (odds['back']['draw']-1) * stakes['back']['draw'] - (odds['lay']['draw']-1)*stakes['lay']['draw']
                if profit > 0:
                    print(Fore.GREEN + f'Opportunity found in {market_name} market' + Style.RESET_ALL)
                    results.append({'type':'draw', 'profit':profit, 'odds':[odds['back']['draw'],odds['lay']['draw']], 'stakes':[100.0, stakes['lay']['draw']]})

        return results if len(results) > 0 else None

    def find_arbitrage(self) -> list :

        results = []

        for sport in self.database:
            for match in self.database[sport]:
                home_team = self.database[sport][match]['home_team']
                away_team = self.database[sport][match]['away_team']
                time = self.database[sport][match]['time']
                for market in self.database[sport][match]['markets']:
                    if market == 'h2h':
                        # Search for h2h arbitrage opportunities
                        calculations = self.run_arb_math(self.database[sport][match]['markets'][market], market)
                        if calculations != None:
                            result = {
                                'id': match,
                                'sport': sport,
                                'type': 'h2h',
                                'home_team': home_team,
                                'away_team': away_team,
                                'time': time,
                                'roi': calculations['roi'],
                                'home_stake': {
                                    'bookmaker': self.database[sport][match]['markets'][market]['homeBest'][1],
                                    'price': self.database[sport][match]['markets'][market]['homeBest'][0],
                                    'stake': calculations['home_stake']
                                },
                                'away_stake': {
                                    'bookmaker': self.database[sport][match]['markets'][market]['awayBest'][1],
                                    'price': self.database[sport][match]['markets'][market]['awayBest'][0],
                                    'stake': calculations['away_stake']
                                }
                            }

                            if 'draw_stake' in calculations:
                                result['draw_stake'] = {
                                    'bookmaker': self.database[sport][match]['markets'][market]['drawBest'][1],
                                    'price': self.database[sport][match]['markets'][market]['drawBest'][0],
                                    'stake': calculations['draw_stake']
                                }

                            results.append(result)

                    elif market == 'totals':
                        # Search for totals arbitrage opportunities
                        calculations = self.run_arb_math(self.database[sport][match]['markets'][market], market)
                        if calculations != None:
                            result = {
                                'id': match,
                                'sport': sport,
                                'type': 'totals',
                                'home_team': home_team,
                                'away_team': away_team,
                                'time': time,
                                'roi': calculations['roi'],
                                'over_stake': {
                                    'bookmaker': self.database[sport][match]['markets'][market]['overBest'][1],
                                    'price': self.database[sport][match]['markets'][market]['overBest'][0],
                                    'stake': calculations['over_stake']
                                },
                                'under_stake': {
                                    'bookmaker': self.database[sport][match]['markets'][market]['underBest'][1],
                                    'price': self.database[sport][match]['markets'][market]['underBest'][0],
                                    'stake': calculations['under_stake']
                                }
                            }

                            results.append(result)

                    elif market == 'h2h_lay':
                        # Search for laybet arbitrage opportunities
                        calculations = self.run_arb_math_laybet(self.database[sport][match]['markets'], market)
                        if calculations != None:

                            result = {
                                'id': match,
                                'sport': sport,
                                'type': 'laybet',
                                'home_team': home_team,
                                'away_team': away_team,
                                'time': time
                            }

                            for calculation in calculations:
                                if calculation['type'] == 'home':
                                    result['home_stake'] = {
                                        'profit': calculation['profit'],
                                        'back_bookmaker': self.database[sport][match]['markets']['h2h']['homeBest'][1],
                                        'lay_bookmaker': self.database[sport][match]['markets'][market]['homeBest'][1],
                                        'back_price': calculation['odds'][0],
                                        'lay_price': calculation['odds'][1],
                                        'lay_stake': calculation['stakes'][1]
                                    }

                                elif calculation['type'] == 'away':
                                    result['away_stake'] = {
                                        'profit': calculation['profit'],
                                        'back_bookmaker': self.database[sport][match]['markets']['h2h']['awayBest'][1],
                                        'lay_bookmaker': self.database[sport][match]['markets'][market]['awayBest'][1],
                                        'back_price': calculation['odds'][0],
                                        'lay_price': calculation['odds'][1],
                                        'lay_stake': calculation['stakes'][1]
                                    }

                                elif calculation['type'] == 'draw':
                                    result['draw_stake'] = {
                                        'profit': calculation['profit'],
                                        'back_bookmaker': self.database[sport][match]['markets']['h2h']['drawBest'][1],
                                        'lay_bookmaker': self.database[sport][match]['markets'][market]['drawBest'][1],
                                        'back_price': calculation['odds'][0],
                                        'lay_price': calculation['odds'][1],
                                        'lay_stake': calculation['stakes'][1]
                                    }

                            results.append(result)

        return results