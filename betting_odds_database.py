# Copyright (c) 2023, Robert Haynes
# All rights reserved.

# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. 

import json

class BettingOddsDatabase:
    database = dict()

    def __init__(self):
        self.database = {
            'americanfootball_cfl': dict(),
            'americanfootball_ncaaf': dict(),
            'americanfootball_nfl': dict(),
            'americanfootball_nfl_super_bowl_winner': dict(),
            'americanfootball_xfl': dict(),
            'aussierules_afl': dict(),
            'baseball_mlb': dict(),
            'baseball_ncaa': dict(),
            'baseball_mlb_preseason': dict(),
            'baseball_mlb_world_series_winner': dict(),
            'basketball_nba': dict(),
            'basketball_euroleague': dict(),
            'basketball_nba_championship_winner': dict(),
            'basketball_wnba': dict(),
            'basketball_ncaab': dict(),
            'cricket_big_bash': dict(),
            'cricket_caribbean_premier_league': dict(),
            'cricket_icc_world_cup': dict(),
            'cricket_international_t20': dict(),
            'cricket_ipl': dict(),
            'cricket_odi': dict(),
            'cricket_psl': dict(),
            'cricket_test_match': dict(),
            'golf_masters_tournament_winner': dict(),
            'golf_pga_championship_winner': dict(),
            'golf_the_open_championship_winner': dict(),
            'golf_us_open_winner': dict(),
            'icehockey_nhl': dict(),
            'icehockey_nhl_championship_winner': dict(),
            'icehockey_sweden_hockey_league': dict(),
            'icehockey_sweden_allsvenskan': dict(),
            'mma_mixed_martial_arts': dict(),
            'politics_us_presidential_election_winner': dict(),
            'rugbyleague_nrl': dict(),
            'soccer_africa_cup_of_nations': dict(),
            'soccer_argentina_primera_division': dict(),
            'soccer_australia_aleague': dict(),
            'soccer_austria_bundesliga': dict(),
            'soccer_belgium_first_div': dict(),
            'soccer_brazil_campeonato': dict(),
            'soccer_brazil_serie_b': dict(),
            'soccer_chile_campeonato': dict(),
            'soccer_china_superleague': dict(),
            'soccer_denmark_superliga': dict(),
            'soccer_efl_champ': dict(),
            'soccer_england_efl_cup': dict(),
            'soccer_england_league1': dict(),
            'soccer_england_league2': dict(),
            'soccer_epl': dict(),
            'soccer_fa_cup': dict(),
            'soccer_fifa_world_cup': dict(),
            'soccer_fifa_world_cup_winner': dict(),
            'soccer_finland_veikkausliiga': dict(),
            'soccer_france_ligue_one': dict(),
            'soccer_france_ligue_two': dict(),
            'soccer_germany_bundesliga': dict(),
            'soccer_germany_bundesliga2': dict(),
            'soccer_germany_liga3': dict(),
            'soccer_greece_super_league': dict(),
            'soccer_italy_serie_a': dict(),
            'soccer_italy_serie_b': dict(),
            'soccer_japan_j_league': dict(),
            'soccer_korea_kleague1': dict(),
            'soccer_league_of_ireland': dict(),
            'soccer_mexico_ligamx': dict(),
            'soccer_netherlands_eredivisie': dict(),
            'soccer_norway_eliteserien': dict(),
            'soccer_poland_ekstraklasa': dict(),
            'soccer_portugal_primeira_liga': dict(),
            'soccer_russia_premier_league': dict(),
            'soccer_spain_la_liga': dict(),
            'soccer_spain_segunda_division': dict(),
            'soccer_spl': dict(),
            'soccer_sweden_allsvenskan': dict(),
            'soccer_sweden_superettan': dict(),
            'soccer_switzerland_superleague': dict(),
            'soccer_turkey_super_league': dict(),
            'soccer_uefa_europa_conference_league': dict(),
            'soccer_uefa_champs_league': dict(),
            'soccer_uefa_europa_league': dict(),
            'soccer_uefa_nations_league': dict(),
            'soccer_conmebol_copa_libertadores': dict(),
            'soccer_usa_mls': dict(),
            'tennis_atp_aus_open_singles': dict(),
            'tennis_atp_french_open': dict(),
            'tennis_atp_us_open': dict(),
            'tennis_atp_wimbledon': dict(),
            'tennis_wta_aus_open_singles': dict(),
            'tennis_wta_french_open': dict(),
            'tennis_wta_us_open': dict(),
            'tennis_wta_wimbledon': dict()
        }

    def formatJSON(self, fileName):
        with open(fileName) as json_file:
            odds_json = json.load(json_file)

        no_draw_sports = ['americanfootball','baseball','icehockey','basketball','golf','tennis','mma','cricket']

        for match in odds_json:
            if type(match) == str:
                continue

            self.database[match['sport_key']][match['id']] = {'home_team': match['home_team'], 'away_team': match['away_team'], 'markets': dict()}

            for bookmaker in match['bookmakers']:
                current_bookmaker = bookmaker['title']

                for odds in bookmaker['markets']:
                    current_market = odds['key']
                    if current_market == 'spreads':
                        continue
                    if current_market not in self.database[match['sport_key']][match['id']]['markets']:

                        if current_market == 'h2h':
                            if any(substring in match['sport_key'] for substring in no_draw_sports):
                                self.database[match['sport_key']][match['id']]['markets']['h2h'] = {'homeBest': [0, ''], 'awayBest': [0, '']}
                            else:
                                self.database[match['sport_key']][match['id']]['markets']['h2h'] = {'homeBest': [0, ''], 'awayBest': [0, ''], 'drawBest': [0, '']}
                        elif current_market == 'totals':
                            self.database[match['sport_key']][match['id']]['markets']['totals'] = {'overBest': [0,odds['outcomes'][0]['point'],''], 'underBest': [0,odds['outcomes'][0]['point'],'']}
                        elif current_market == 'h2h_lay':
                            if any(substring in match['sport_key'] for substring in no_draw_sports):
                                self.database[match['sport_key']][match['id']]['markets']['h2h_lay'] = {'homeBest': [0, ''], 'awayBest': [0, '']}
                            else:
                                self.database[match['sport_key']][match['id']]['markets']['h2h_lay'] = {'homeBest': [0, ''], 'awayBest': [0, ''], 'drawBest': [0, '']}
                        
                    for outcomes in odds['outcomes']:
                        if current_market == 'h2h':
                            if current_bookmaker == 'Betfair' or current_bookmaker == 'Matchbook':
                                continue
                            if outcomes['name'] == match['home_team']:
                                home_price = outcomes['price']
                                if home_price > self.database[match['sport_key']][match['id']]['markets'][current_market]['homeBest'][0]:
                                    self.database[match['sport_key']][match['id']]['markets'][current_market]['homeBest'] = [home_price, current_bookmaker]

                            elif outcomes['name'] == match['away_team']:
                                away_price = outcomes['price']
                                if away_price > self.database[match['sport_key']][match['id']]['markets'][current_market]['awayBest'][0]:
                                    self.database[match['sport_key']][match['id']]['markets'][current_market]['awayBest'] = [away_price, current_bookmaker]

                            elif outcomes['name'] == 'Draw':
                                draw_price = outcomes['price']
                                if draw_price > self.database[match['sport_key']][match['id']]['markets'][current_market]['drawBest'][0]:
                                    self.database[match['sport_key']][match['id']]['markets'][current_market]['drawBest'] = [draw_price, current_bookmaker]

                        elif current_market == 'totals':
                            price = outcomes['price']
                            point = outcomes['point']

                            if outcomes['name'] == 'Over':
                                if price > self.database[match['sport_key']][match['id']]['markets'][current_market]['overBest'][0] and point == self.database[match['sport_key']][match['id']]['markets'][current_market]['overBest'][1]:
                                    self.database[match['sport_key']][match['id']]['markets'][current_market]['overBest'] = [price, point, current_bookmaker]

                            elif outcomes['name'] == 'Under':
                                if price > self.database[match['sport_key']][match['id']]['markets'][current_market]['underBest'][0] and point == self.database[match['sport_key']][match['id']]['markets'][current_market]['overBest'][1]:
                                    self.database[match['sport_key']][match['id']]['markets'][current_market]['underBest'] = [price, point, current_bookmaker]

                        if current_market == 'h2h_lay':
                            if outcomes['name'] == match['home_team']:
                                home_price = outcomes['price']
                                if home_price > self.database[match['sport_key']][match['id']]['markets'][current_market]['homeBest'][0]:
                                    self.database[match['sport_key']][match['id']]['markets'][current_market]['homeBest'] = [home_price, current_bookmaker]

                            elif outcomes['name'] == match['away_team']:
                                away_price = outcomes['price']
                                if away_price > self.database[match['sport_key']][match['id']]['markets'][current_market]['awayBest'][0]:
                                    self.database[match['sport_key']][match['id']]['markets'][current_market]['awayBest'] = [away_price, current_bookmaker]

                            elif outcomes['name'] == 'Draw':
                                draw_price = outcomes['price']
                                if draw_price > self.database[match['sport_key']][match['id']]['markets'][current_market]['drawBest'][0]:
                                    self.database[match['sport_key']][match['id']]['markets'][current_market]['drawBest'] = [draw_price, current_bookmaker]