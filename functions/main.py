# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_functions import params
from firebase_functions.firestore_fn import (
    on_document_created,
    Event,
    DocumentSnapshot
)
from firebase_admin import initialize_app

import requests

# initialize_app()

DISCORD_WEBWHOOK_URL = params.SecretParam('DISCORD_WEBHOOK_URL')

def post_message_to_discord(bot_name: str, message_body: str, webhook_url: str) -> requests.Response:

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


@on_document_created(region='europe-west1', secrets=[DISCORD_WEBWHOOK_URL], document='h2h/{id}')
def send_notification_on_h2h(event: Event[DocumentSnapshot]) -> None :

    bet = event.data.to_dict()

    sport = bet['sport']
    time = bet['time']
    home_team = bet['home_team']
    away_team = bet['away_team']
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

    try:
        # [START v2SendToDiscord]
        response = post_message_to_discord(
            "Arb Bot", message, DISCORD_WEBWHOOK_URL.value
        )
        if response.ok:
            print(f"Posted bet @{event.data.id} to Discord.")
        else:
            response.raise_for_status()
        # [END v2SendToDiscord]
    except (EnvironmentError, requests.HTTPError) as error:
        print(f"Unable to post fatal Arb bet @{event.data.id} to Discord.", error)

@on_document_created(region='europe-west1', secrets=[DISCORD_WEBWHOOK_URL], document='laybet/{id}')
def send_notification_on_laybet(event: Event[DocumentSnapshot]) -> None :

    bet = event.data.to_dict()

    sport = bet['sport']
    time = bet['time']
    home_team = bet['home_team']
    away_team = bet['away_team']
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
        response = post_message_to_discord(
            "Arb Bot", message, DISCORD_WEBWHOOK_URL.value
        )
        if response.ok:
            print(f"Posted bet @{event.data.id} to Discord.")
        else:
            response.raise_for_status()
        # [END v2SendToDiscord]
    except (EnvironmentError, requests.HTTPError) as error:
        print(f"Unable to post fatal Arb bet @{event.data.id} to Discord.", error)

@on_document_created(region='europe-west1', secrets=[DISCORD_WEBWHOOK_URL], document='totals/{id}')
def send_notification_on_totals(event: Event[DocumentSnapshot]) -> None :
    
    bet = event.data.to_dict()

    sport = bet['sport']
    time = bet['time']
    home_team = bet['home_team']
    away_team = bet['away_team']
    stakes = {'over': bet['over_stake'], 'under': bet['under_stake']}

    message = f"""
## 💎 New Totals Opportunity 💎

**Sport:** {sport}
**Match:** {home_team} vs {away_team} at {time}
**Stakes:**
    *Over:* Stake £{stakes['over']['stake']} with {stakes['over']['bookmaker']} @ {stakes['over']['price']}
    *Under:* Stake £{stakes['under']['stake']} with {stakes['under']['bookmaker']} @ {stakes['under']['price']}

for a return of {bet['roi']}%
""".strip()
        
    try:
        # [START v2SendToDiscord]
        response = post_message_to_discord(
            "Arb Bot", message, DISCORD_WEBWHOOK_URL.value
        )
        if response.ok:
            print(f"Posted bet @{event.data.id} to Discord.")
        else:
            response.raise_for_status()
        # [END v2SendToDiscord]
    except (EnvironmentError, requests.HTTPError) as error:
        print(f"Unable to post fatal Arb bet @{event.data.id} to Discord.", error)


