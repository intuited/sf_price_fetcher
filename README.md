# `sf_price_fetcher`

Simple Python API to pull pricing information from scryfall.com.

Provides caching of prices via an sqlite3 database.

*NOTE* that currently (as of v.0.1), the cache expiry time is set to 1 week.
This will change and become configurable in future versions.

### Usage

Typical usage is quite straightforward:

    >>> from sf_price_fetcher import fetcher
    >>> fetcher.get('mox amber')
    '29.98'

`sf_price_fetcher` returns the lowest USD price for any printing of that card
which is not from a promotional set.

### CLI

`sf_price_fetcher` also includes a command-line interface.  For syntax information:

    $ python -m sf_price_fetcher --help
    usage: __main__.py [-h] [-c] [-s] card_name

    Card price fetcher for scryfall.com

    positional arguments:
      card_name

    optional arguments:
      -h, --help    show this help message and exit
      -c, --card    Print full card data instead of just the price.
      -s, --search  Search for the card name and return all unique printings.

Usage examples:

    $ python -m sf_price_fetcher faerie\ vandal
    faerie vandal: $0.07
    $ python -m sf_price_fetcher "black lotus"
    black lotus: $8499.99

The `-c` and `-s` options are primarily used for debugging.
They output the full JSON data pulled from scryfall.

    $ python -m sf_price_fetcher -c 'blacker lotus' | head
    {'object': 'card',
     'id': '4c85d097-e87b-41ee-93c6-0e54ec41b174',
     'oracle_id': '41dd29b9-f08d-4ccc-8dc0-da11d2d456e9',
     'multiverse_ids': [9764],
     'tcgplayer_id': 830,
     'cardmarket_id': 11870,
     'name': 'Blacker Lotus',
     'lang': 'en',
     'released_at': '1998-08-11',
     'uri': 'https://api.scryfall.com/cards/4c85d097-e87b-41ee-93c6-0e54ec41b174',
