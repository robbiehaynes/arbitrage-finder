import requests
import json
import credentials

# An api key is emailed to you when you sign up to a plan
# Get a free API key at https://api.the-odds-api.com/
API_KEY = credentials.API_KEY_SERVICE

SPORT = 'soccer_austria_bundesliga' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

REGIONS = 'uk' # uk | us | eu | au. Multiple can be specified if comma delimited

MARKETS = 'h2h,spreads,totals' # h2h | spreads | totals. Multiple can be specified if comma delimited

ODDS_FORMAT = 'decimal' # decimal | american

DATE_FORMAT = 'iso' # iso | unix

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
#   Function to call the /sports endpoint to get a list of in season sports
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# sports_response = requests.get('https://api.the-odds-api.com/v4/sports', params={
#     'api_key': API_KEY
# })


# if sports_response.status_code != 200:
#     print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

# else:
#     print('List of in season sports:', sports_response.json())



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# Now get a list of live & upcoming games for the sport you want, along with odds for different bookmakers
# This will deduct from the usage quota
# The usage quota cost = [number of markets specified] x [number of regions specified]
# For examples of usage quota costs, see https://the-odds-api.com/liveapi/guides/v4/#usage-quota-costs
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds', params={
    'api_key': API_KEY,
    'regions': REGIONS,
    'markets': MARKETS,
    'oddsFormat': ODDS_FORMAT,
    'dateFormat': DATE_FORMAT,
})

if odds_response.status_code != 200:
    print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

else:
    odds_json = odds_response.json()
    print('Number of events:', len(odds_json))
    print(odds_json)

    with open('odds.json', 'w') as outfile:
        json.dump(odds_json, outfile)

    # Check the usage quota
    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])