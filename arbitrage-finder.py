# Copyright (c) 2023, Robert Haynes
# All rights reserved.

# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. 

import arbmath
import json
from networkhandler import OddsAPIHandler as api
from networkhandler import FirebaseHandler
from betting_odds_database import BettingOddsDatabase as db
from colorama import Fore, Back, Style

if __name__ == "__main__":
    print(Back.MAGENTA + "       Welcome to the Arbitrage Finder!       " + Style.RESET_ALL)
    print(Fore.MAGENTA + "This program will find arbitrage opportunities for you." + Style.RESET_ALL +"\n")
    
    database = db()

    print(Fore.YELLOW + "Formatting JSON data..." + Style.RESET_ALL)
    database.formatJSON('football_austria_odds.json')
    database.formatJSON('all_us_odds.json')
    database.formatJSON('all_mls_odds.json')
    print(Back.GREEN + Fore.BLACK + "Formatting complete!\n" + Style.RESET_ALL)

    

    with open('allOdds.json', 'w') as outfile:
        json.dump(database.database, outfile, indent=4)

    print(Fore.YELLOW + "Finding arbitrage opportunities..." + Style.RESET_ALL)
    with open('all_arbs.json', 'w') as outfile:
        json.dump(arbmath.find_arbitrage(database.database), outfile, indent=4)
    print(Back.GREEN + Fore.BLACK + "Searching complete!" + Style.RESET_ALL + "\n")

    print(Fore.YELLOW + "Uploading arbitrage opportunities to Firestore..." + Style.RESET_ALL)
    bets = []
    handler = FirebaseHandler()

    with open('all_arbs.json', 'r') as outfile:
        bets = json.load(outfile)

    for bet in bets:
        handler.addOddsToFirebase(bet)
    print(Back.GREEN + Fore.BLACK + "Upload complete!" + Style.RESET_ALL + "\n")

    # with open('all_mls_odds.json', 'w') as outfile:
    #     json.dump(fetchFromAPI(), outfile)

    sports = ['americanfootball_cfl', 'americanfootball_ncaaf', 'americanfootball_nfl', 'americanfootball_nfl_super_bowl_winner', 'americanfootball_xfl', 'aussierules_afl', 'baseball_mlb', 'baseball_ncaa', 'baseball_mlb_preseason', 'baseball_mlb_world_series_winner', 'basketball_nba', 'basketball_euroleague', 'basketball_nba_championship_winner', 'basketball_wnba', 'basketball_ncaab', 'cricket_big_bash', 'cricket_caribbean_premier_league', 'cricket_icc_world_cup', 'cricket_international_t20', 'cricket_ipl', 'cricket_odi', 'cricket_psl', 'cricket_test_match', 'golf_masters_tournament_winner', 'golf_pga_championship_winner', 'golf_the_open_championship_winner', 'golf_us_open_winner', 'icehockey_nhl', 'icehockey_nhl_championship_winner', 'icehockey_sweden_hockey_league', 'icehockey_sweden_allsvenskan', 'mma_mixed_martial_arts', 'politics_us_presidential_election_winner', 'rugbyleague_nrl', 'soccer_africa_cup_of_nations', 'soccer_argentina_primera_division', 'soccer_australia_aleague', 'soccer_austria_bundesliga', 'soccer_belgium_first_div', 'soccer_brazil_campeonato', 'soccer_brazil_serie_b', 'soccer_chile_campeonato', 'soccer_china_superleague', 'soccer_denmark_superliga', 'soccer_efl_champ', 'soccer_england_efl_cup', 'soccer_england_league1', 'soccer_england_league2', 'soccer_epl', 'soccer_fa_cup', 'soccer_fifa_world_cup', 'soccer_fifa_world_cup_winner', 'soccer_finland_veikkausliiga', 'soccer_france_ligue_one', 'soccer_france_ligue_two', 'soccer_germany_bundesliga', 'soccer_germany_bundesliga2', 'soccer_germany_liga3', 'soccer_greece_super_league', 'soccer_italy_serie_a', 'soccer_italy_serie_b', 'soccer_japan_j_league', 'soccer_korea_kleague1', 'soccer_league_of_ireland', 'soccer_mexico_ligamx', 'soccer_netherlands_eredivisie', 'soccer_norway_eliteserien', 'soccer_poland_ekstraklasa', 'soccer_portugal_primeira_liga', 'soccer_russia_premier_league', 'soccer_spain_la_liga', 'soccer_spain_segunda_division', 'soccer_spl', 'soccer_sweden_allsvenskan', 'soccer_sweden_superettan', 'soccer_switzerland_superleague', 'soccer_turkey_super_league', 'soccer_uefa_europa_conference_league', 'soccer_uefa_champs_league', 'soccer_uefa_europa_league', 'soccer_uefa_nations_league', 'soccer_conmebol_copa_libertadores', 'soccer_usa_mls', 'tennis_atp_aus_open_singles', 'tennis_atp_french_open', 'tennis_atp_us_open', 'tennis_atp_wimbledon', 'tennis_wta_aus_open_singles', 'tennis_wta_french_open', 'tennis_wta_us_open', 'tennis_wta_wimbledon']