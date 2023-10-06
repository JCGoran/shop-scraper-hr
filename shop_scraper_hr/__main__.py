from pprint import pprint

from shop_scraper_hr import konzum, tommy

if __name__ == "__main__":
    prices = konzum.get_all_prices(timeout=10)
    pprint(prices, indent=4)
