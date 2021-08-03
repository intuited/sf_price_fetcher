"""sf_price_fetcher

Fetches MTG card prices from Scryfall

- As per API documentation, waits 100ms between requests
- TODO: Timestamps price retrieval per card, caches it for 24h
"""
import requests
import time
import sys
import json
import pprint
from functools import partial
pp = partial(pprint.pprint, sort_dicts=False)

class Fetcher:
    last_request = 0      # timestamp of last retrieval
    min_interval = 100000 # minimum interval between requests in ns

    api_url = 'https://api.scryfall.com/cards/named'

    def get(self, card_name, timeout=2.0):
        """Fetch pricing data for card `card_name`.

        Blocks until self.last_request + 100ms.

        Then updates self.last_request and requests pricing data from Scryfall.

        Times out if no response is received within `timeout` seconds.
        """
        now = time.monotonic_ns()
        if now - self.last_request < self.min_interval:
            time.sleep((now - self.last_request) / 1000000.0)

        r = requests.get(self.api_url, {'exact': card_name})
        j = json.loads(r.text)
        return j['prices']['usd']

fetcher = Fetcher() # singleton object to restrict retrieval frequency

if __name__ == '__main__':
    card_name = sys.argv[1]
    price = fetcher.get(card_name)
    print(f'{card_name}: ${price}')
