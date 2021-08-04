import sys, argparse
from sf_price_fetcher import fetcher, pp

def print_price(card_name):
    price = fetcher.get(card_name)
    print(f'{card_name}: ${price}')

def print_card(card_name):
    pp(fetcher.get_card(card_name))

def search_card(card_name):
    pp(fetcher.search_card_name(card_name))

argparser = argparse.ArgumentParser(description='Card price fetcher for scryfall.com')
argparser.add_argument('-c', '--card', dest='action', action='store_const',
                       const=print_card, default=print_price,
                       help='Print full card data instead of just the price.')
argparser.add_argument('-s', '--search', dest='action', action='store_const',
                       const=search_card, default=print_price,
                       help='Search for the card name and return all unique printings.')

argparser.add_argument('card_name', type=str)
args = argparser.parse_args()

args.action(args.card_name)
