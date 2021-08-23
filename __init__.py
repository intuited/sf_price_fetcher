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
import datetime
from sf_price_fetcher import lookups
pp = partial(pprint.pprint, sort_dicts=False)

class SFException(Exception):
    pass

debug = lambda *args, **kwargs: None
#debug = print

log = print

class Fetcher:
    last_request = 0      # timestamp of last retrieval
    min_interval = 100000 # minimum interval between requests in ns

    api_url = 'https://api.scryfall.com/cards/named'

    def get(self, card_name, timeout=5.0, use_db=True):
        """Fetch pricing data for card `card_name`.

        If there's current pricing in the cache, returns the cached price.

        Otherwise, fetches the current price, adds it to the db,
        and returns result of `find_card_name`.

        If `use_db` is False, skip both checking the cache and updating the db.
        """
        # check the lookups db for a sufficiently recent record
        if use_db:
            price = lookups.cache_check(card_name)
            if price is not False:
                debug(f'Cache hit for "{card_name}": ${price:.2f}')
                return price

        card = self.find_card_name(card_name, timeout=timeout)
        price = float(card['prices']['usd'])

        if use_db:
            lookups.add(card_name, price)

        return price

    def get_card(self, card_name, timeout=5.0):
        """Fetch info for card `card_name` using the API name url.

        Returns full parsed JSON for the card name.
        """
        r = self.request(self.api_url, {'exact': card_name}, timeout=timeout)
        return json.loads(r.text)

    def search_card_name(self, card_name, timeout=5.0):
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

    def find_card_name(self, card_name, timeout=5.0):
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

    def request(self, url, params, timeout=5.0):
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

    def update_prices(self, card_name, timeout=5.0):
        """Updates pricing information for all cards in db.

        If the fetched price differs from the cached price,
        stores the fetched price in the db.

        Otherwise, if there is only one stored price for the card name,
        adds a second record containing the new price.

        If there are multiple records, update the timestamp of the
        most recent one.

        Given sufficiently frequent execution of this routine,
        this will allow price changes to be tracked using the db data.
        """
        log(f'----DB update {datetime.datetime.now()}----')
        cards = lookups.all_cards()
        if card_name == None:
            for name, records in cards.items():
                self.update_card_price(name, records)
        else:
            self.update_card_price(card_name, cards[card_name])

    def update_card_price(self, name, records):
        """Subroutine that handles price updating for a single card name."""
        name = name.lower()
        last_time, last_price = records[-1]
        last_price = last_price
        log(f'__{name}__: fetching current price...')
        now = datetime.datetime.now()
        price = self.get(name, use_db=False)
        if price != last_price:
            log(f'__{name}__: Price changed: ${last_price:.2f} -> ${price:.2f}.  Adding new db entry.')
            lookups.add(name, price)
        elif len(records) == 1:
            log(f'__{name}__: Adding second db entry for stable price ${price:.2f}.')
            lookups.add(name, price)
        else:
            log(f'__{name}__: Price unchanged from ${price:.2f}.  Updating timestamp for record with timestamp {last_time}.')
            lookups.update_timestamp(name, last_time, now)

fetcher = Fetcher() # singleton object to restrict retrieval frequency
