"""sf_price_fetcher

Fetches MTG card prices from Scryfall

- As per API documentation, waits 100ms between requests
- TODO: Timestamps price retrieval per card, caches it for 24h
"""
import requests
import time
import json
import pprint
from functools import partial
pp = partial(pprint.pprint, sort_dicts=False)

class Fetcher:
    last_request = 0      # timestamp of last retrieval
    min_interval = 100000 # minimum interval between requests in ns

    api_url = 'https://api.scryfall.com/cards/named'

    def get(self, card_name, timeout=2.0):
        """Fetch pricing data for card `card_name`."""
        j = self.get_card(card_name, timeout=timeout)
        return j['prices']['usd']

    def get_card(self, card_name, timeout=2.0):
        """Fetch info for card `card_name`

        Blocks until self.last_request + 100ms.

        Then updates self.last_request and requests pricing data from Scryfall.

        Times out if no response is received within `timeout` seconds.

        Returns parsed JSON data.
        """
        now = time.monotonic_ns()
        if now - self.last_request < self.min_interval:
            time.sleep((now - self.last_request) / 1000000.0)

        self.last_request = now
        r = requests.get(self.api_url, {'exact': card_name})
        return json.loads(r.text)

fetcher = Fetcher() # singleton object to restrict retrieval frequency
