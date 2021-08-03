import sys
from sf_price_fetcher import fetcher

if __name__ == '__main__':
    card_name = sys.argv[1]
    price = fetcher.get(card_name)
    print(f'{card_name}: ${price}')
