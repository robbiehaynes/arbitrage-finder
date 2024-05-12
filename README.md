# Python Arbitrage Betting Finder :chart_with_upwards_trend:

This arbitrage betting finder will search major sports events, using [The Odds API](https://the-odds-api.com) to fetch odds.

Then, using clever mathematics, will search for arbitrage opportunities across all bookmakers.

## How to use

```
python arbitrage-finder.py
```

This will return:
- Matches with arbitrage opportunities
- Correct odds to use
- Amount to wager on each result
- Bookmaker to use

_To save the arbitrage opportunities to a custom datastore, update the APIHandler in the networkhandler.py to use your storage solution. Also please add a DISCORD_WEBHOOK_URL in your env variables if you wish to use this feature_


**Disclaimer: Arbitrage betting discussed herein is purely for educational purposes and should not be construed as financial advice.**
