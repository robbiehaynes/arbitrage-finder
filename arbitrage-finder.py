# Copyright (c) 2023, Robert Haynes
# All rights reserved.

# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. 

import arbmath
import json
import os
from networkhandler import OddsAPIHandler as oddsapi
from networkhandler import FirebaseHandler
from betting_odds_database import BettingOddsDatabase as db
from colorama import Fore, Back, Style

if __name__ == "__main__":
    print(Back.MAGENTA + "       Welcome to the Arbitrage Finder!       " + Style.RESET_ALL)
    print(Fore.MAGENTA + "This program will find arbitrage opportunities for you." + Style.RESET_ALL +"\n")
    
    database = db()
    odds_api = oddsapi('basketball_nba')

    print(Fore.YELLOW + "Fetching odds from API..." + Style.RESET_ALL)
    with open('data/sports.txt', 'r') as f:
        for line in f:
            if line[0] != '#':
                odds_api.SPORT = line.strip()
                with open('odds/'+odds_api.SPORT+'.json', 'w') as output:
                    json.dump(odds_api.fetchFromAPI(), output)
    print(Back.GREEN + Fore.BLACK + "Odds received!\n" + Style.RESET_ALL)

    print(Fore.YELLOW + "Formatting JSON data..." + Style.RESET_ALL)
    for filename in os.listdir('odds'):
        database.formatJSON('odds/'+filename)
    print(Back.GREEN + Fore.BLACK + "Formatting complete!\n" + Style.RESET_ALL)

    

    with open('data/allOdds.json', 'w') as outfile:
        json.dump(database.database, outfile, indent=4)

    print(Fore.YELLOW + "Finding arbitrage opportunities..." + Style.RESET_ALL)
    with open('data/all_arbs.json', 'w') as outfile:
        json.dump(arbmath.find_arbitrage(database.database), outfile, indent=4)
    print(Back.GREEN + Fore.BLACK + "Searching complete!" + Style.RESET_ALL + "\n")

    print(Fore.YELLOW + "Uploading arbitrage opportunities to Firestore..." + Style.RESET_ALL)
    bets = []
    handler = FirebaseHandler()

    with open('data/all_arbs.json', 'r') as outfile:
        bets = json.load(outfile)

    for bet in bets:
        handler.addOddsToFirebase(bet)
    print(Back.GREEN + Fore.BLACK + "Upload complete!" + Style.RESET_ALL + "\n")

    # with open('all_mls_odds.json', 'w') as outfile:
    #     json.dump(fetchFromAPI(), outfile)
