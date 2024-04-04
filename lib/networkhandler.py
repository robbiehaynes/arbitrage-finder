import requests
import os
from dotenv import load_dotenv, find_dotenv
from dateutil import parser
from colorama import Fore, Back, Style

load_dotenv(find_dotenv('.env.local'))

class OddsAPIHandler:
    # An api key is emailed to you when you sign up to a plan
    # Get a free API key at https://api.the-odds-api.com/
    API_KEY = os.getenv('ODDS_API_KEY')

    SPORT = 'soccer_usa_mls' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

    REGIONS = 'uk' # uk | us | eu | au. Multiple can be specified if comma delimited

    MARKETS = 'h2h,totals' # h2h | spreads | totals. Multiple can be specified if comma delimited

    ODDS_FORMAT = 'decimal' # decimal | american

    DATE_FORMAT = 'iso' # iso | unix

    def __init__(self, sport, markets = 'h2h,totals', odds_format = 'decimal', date_format = 'iso'):
        self.SPORT = sport
        self.MARKETS = markets
        self.ODDS_FORMAT = odds_format
        self.DATE_FORMAT = date_format

    def fetchFromAPI(self):
        print(Fore.YELLOW + f'Getting the {self.SPORT} odds from API...' + Style.RESET_ALL)

        odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{self.SPORT}/odds', params={
            'api_key': self.API_KEY,
            'regions': self.REGIONS,
            'markets': self.MARKETS,
            'oddsFormat': self.ODDS_FORMAT,
            'dateFormat': self.DATE_FORMAT,
        })

        if odds_response.status_code != 200:
            print(Back.RED + f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}' + Style.RESET_ALL)

        else:
            odds_json = odds_response.json()
            print(Fore.GREEN + 'Number of events received:', len(odds_json))
            print(Style.RESET_ALL)

            # Update the usage quota
            print('Remaining requests', odds_response.headers['x-requests-remaining'])
            print('Used requests', odds_response.headers['x-requests-used'])
        
        return odds_json
    
    def print_quota(self):
        response = requests.get('https://api.the-odds-api.com/v4/sports', params={
            'api_key': self.API_KEY
        })

        if response.status_code != 200:
            print(Back.RED + f'Failed to get quota: status_code {response.status_code}, response body {response.text}' + Style.RESET_ALL)

        else:
            # Print the usage quota
            print('Remaining requests', response.headers['x-requests-remaining'])
            print('Used requests', response.headers['x-requests-used'])
    
class APIHandler:

    def __init__(self):
        self.auth_token = self.get_auth_token()

    @staticmethod
    def get_auth_token():
        url = "https://arbfiner.uk.auth0.com/oauth/token"

        payload = {
            "client_id": os.getenv('CLIENT_ID'),
            "client_secret": os.getenv('CLIENT_SECRET'),
            "audience": "https://arbitrage-finder",
            "grant_type": "client_credentials"
        }

        headers = {
            'content-type': "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            print(Back.RED + f'Failed to get auth token: status_code {response.status_code}, response body {response.text}' + Style.RESET_ALL)
            return None
        else:
            return response.json()['access_token']

    def post_odds_to_database(self, bet_json):

        endpoint = os.getenv('API_ENDPOINT')

        header = {
            'Authorization': f'Bearer {self.auth_token}'
        }

        response = requests.post(endpoint, json=bet_json, headers=header)

        if response.status_code not in [200, 201]:
            print(Back.RED + f'Failed to post odds to database: status_code {response.status_code}, response body {response.json()["message"]}' + Style.RESET_ALL)
            return None
        else:
            print(Fore.GREEN + 'Odds posted to database!' + Style.RESET_ALL)
            return response.json()["data"]["_id"]
    
class DiscordHandler:

    def __init__(self) -> None:
        self.DISCORD_WEBWHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

    @staticmethod
    def _send_post_request(bot_name: str, message_body: str, webhook_url: str) -> requests.Response:

        if webhook_url == "":
            raise EnvironmentError(
                "No webhook URL found. Set the Discord Webhook URL before deploying. "
                "Learn more about Discord webhooks here: "
                "https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks"
            )
        
        return requests.post(
            url=webhook_url,
            json={
                'username': bot_name,
                'content': message_body
            }
        )

    def send_bet_to_discord(self, bet: dict, bet_id: str) -> None :

        sport = bet['sport']
        time = bet['time']
        home_team = bet['home_team']
        away_team = bet['away_team']

        if bet['type'] == 'h2h':
            stakes = {'home': bet['home_stake'], 'away': bet['away_stake']}
            message = f"""
    ## 💎 New Head 2 Head Opportunity 💎

    **Sport:** {sport}
    **Match:** {home_team} vs {away_team} at {time}
    **Stakes:**
        *Home:* Stake £{stakes['home']['stake']} with {stakes['home']['bookmaker']} @ {stakes['home']['price']}
        *Away:* Stake £{stakes['away']['stake']} with {stakes['away']['bookmaker']} @ {stakes['away']['price']}

    for a return of {bet['roi']}%
    """.strip()
        elif bet['type'] == 'totals':
            stakes = {'over': bet['over_stake'], 'under': bet['under_stake']}
            message = f"""
        ## 💎 New Totals Opportunity 💎

        **Sport:** {sport}
        **Match:** {home_team} vs {away_team} at {time}
        **Stakes:**
            *Over {stakes['over']['point']}:* Stake £{stakes['over']['stake']} with {stakes['over']['bookmaker']} @ {stakes['over']['price']}
            *Under {stakes['under']['point']}:* Stake £{stakes['under']['stake']} with {stakes['under']['bookmaker']} @ {stakes['under']['price']}

        for a return of {bet['roi']}%
        """.strip()
        else:
            stakes = {}
            message = f"""
        ## 💎 New Laybet Opportunity 💎

        **Sport:** {sport}
        **Match:** {home_team} vs {away_team} at {time}
        **Stakes:** """

            if 'home_stake' in bet:
                stakes['home'] = bet['home_stake']
                message += f""" 
            *Home:*     Back Stake £100 with {stakes['home']['back_bookmaker']} @ {stakes['home']['back_price']}
                        Lay Stake £{stakes['home']['lay_stake']} with {stakes['home']['lay_bookmaker']} @ {stakes['home']['lay_price']}
                        for a profit of £{stakes['home']['profit']}"""
            elif 'away_stake' in bet:
                stakes['away'] = bet['away_stake']
                message += f""" 
            *Away:*     Back Stake £100 with {stakes['away']['back_bookmaker']} @ {stakes['away']['back_price']}
                        Lay Stake £{stakes['away']['lay_stake']} with {stakes['away']['lay_bookmaker']} @ {stakes['away']['lay_price']}
                        for a profit of £{stakes['away']['profit']}"""
            elif 'draw_stake' in bet:
                stakes['draw']= bet['draw_stake']
                message += f""" 
            *Draw:*     Back Stake £100 with {stakes['draw']['back_bookmaker']} @ {stakes['draw']['back_price']}
                        Lay Stake £{stakes['draw']['lay_stake']} with {stakes['draw']['lay_bookmaker']} @ {stakes['draw']['lay_price']}
                        for a profit of £{stakes['draw']['profit']}"""

            message.strip()

        try:
            # [START v2SendToDiscord]
            response = self._send_post_request(
                "Arb Bot", message, self.DISCORD_WEBWHOOK_URL
            )
            if response.ok:
                print(f"Posted bet @{bet_id} to Discord.")
            else:
                response.raise_for_status()
            # [END v2SendToDiscord]
        except (EnvironmentError, requests.HTTPError) as error:
            print(f"Unable to post fatal Arb bet @{bet_id} to Discord.", error)