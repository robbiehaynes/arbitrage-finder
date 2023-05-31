import credentials
import requests
import firebase_admin
from dateutil import parser
from firebase_admin import credentials as firebase_credentials
from firebase_admin import firestore
from colorama import Fore, Back, Style

class OddsAPIHandler:
    # An api key is emailed to you when you sign up to a plan
    # Get a free API key at https://api.the-odds-api.com/
    API_KEY = credentials.API_KEY_SERVICE

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
    
class FirebaseHandler:

    db = None

    def __init__(self):
        cred = firebase_credentials.Certificate('credentials/firebaseServiceAccountKey.json')
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def addOddsToFirebase(self, bet_json):
        bet_json['time'] = parser.parse(bet_json['time'])
        id = bet_json['id']
        del bet_json['id']

        try:
            self.db.collection(bet_json['type']).document(id).set(bet_json)
        except Exception as e:
            print(Back.RED + f'Failed to add odds to Firebase: {e}' + Style.RESET_ALL)

    def fetchFromFirebase(self):
        print(Fore.YELLOW + 'Getting the odds from Firebase...' + Style.RESET_ALL)