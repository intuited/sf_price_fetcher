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

class SFException(Exception):
    pass

debug = print
debug = lambda *args, **kwargs: None

#debug = lambda *args, **kwargs: print(*args, **kwargs)

class Fetcher:
    last_request = 0      # timestamp of last retrieval
    min_interval = 100000 # minimum interval between requests in ns

    api_url = 'https://api.scryfall.com/cards/named'

    def get(self, card_name, timeout=2.0):
        """Fetch pricing data for card `card_name`.

        Retrieves data for all printings with that exact name (case insensitive).

        """
        j = self.find_card_name(card_name, timeout=timeout)
        return j['prices']['usd']

    def get_card(self, card_name, timeout=2.0):
        """Fetch info for card `card_name` using the API name url.

        Returns full parsed JSON for the card name.
        """
        r = self.request(self.api_url, {'exact': card_name}, timeout=timeout)
        return json.loads(r.text)

    def search_card_name(self, card_name, timeout=2.0):
        """Search via the scryfall API for all printings of an exact card name.

        Returns English results only.

        Results are sorted by USD value from high to null.
        """
        r = self.request('https://api.scryfall.com/cards/search',
                         {'unique': 'prints',
                          'order': 'usd',
                          'q': f'lang:en !"{card_name}"'},
                         timeout=timeout)
        j = json.loads(r.text)
        if 'data' not in j:
            raise SFException(f'Invalid card name "{card_name}".')

        return j['data']

    def find_card_name(self, card_name, timeout=2.0):
        """Calls `search_card_name` and trims results to cheapest valid printing.

        Filters out any results for which 'set_type' is 'promo' or for which there is no usd price.

        Returns the last (lowest-priced) result.
        """
        printings = self.search_card_name(card_name, timeout=timeout)

        printings = [card for card in printings
                     if card['set_type'] != 'promo' and card['prices']['usd'] is not None]
        if not printings:
            raise SFException(f'No valid results for card name "{card_name}"')
        return printings[-1]

    def request(self, url, params, timeout=2.0):
        """Make a request from the scryfall REST API.

        Blocks until the time of self.last_request + 100ms.

        Then updates self.last_request and sends request.

        Times out if no response is received within `timeout` seconds.

        Returns parsed JSON data.
        """
        now = time.monotonic_ns()
        if now - self.last_request < self.min_interval:
            time.sleep((now - self.last_request) / 1000000.0)

        self.last_request = now
        r = requests.get(url, params, timeout=timeout)
        debug(f'Fetcher.request called.  url: {r.url}')
        return r

fetcher = Fetcher() # singleton object to restrict retrieval frequency
