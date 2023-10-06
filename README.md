This is a simple scraper for obtaining the prices of goods in Croatian supermarkets.
Inspired by [this post](https://mastodon.gamedev.place/@badlogic/111071396799790275).

# Supported sites

See [`shop_scraper_hr/scrapers`](shop_scraper_hr/scrapers) for a list of supported scrapers.

# Installation

## Release version

```sh
pip install shop-scraper-hr
```

## Dev version

Clone the repo:
```sh
git clone git@github.com:JCGoran/shop-scraper-hr.git
```

The project uses [Python Poetry](https://python-poetry.org/) for dependency management, and all dependencies can be installed using:

```sh
poetry install
```

# Usage

```python
>>> # for getting data from Konzum
>>> from shop_scraper_hr.scrapers import konzum
>>> # get a list of all categories
>>> categories = konzum.get_category_urls()
>>> # get a list of prices from a category
>>> prices = konzum.get_prices(categories[0])
>>> prices
[
    {   'currency_per_unit_quantity': '€/kom',
        'price_data': {   'amount': '1,72',
                          'currency': '€',
                          'quantity_unit': 'kom'},
        'price_fractional_part': 72,
        'price_integer_part': 1,
        'title': 'F5 Auto spužva jumbo',
        'url': 'https://www.konzum.hr/web/products/f5-auto-spuzva-jumbo'},
    {   'currency_per_unit_quantity': '€/kom',
        'price_data': {   'amount': '5,31',
                          'currency': '€',
                          'quantity_unit': 'kom'},
        'price_fractional_part': 31,
        'price_integer_part': 5,
        'title': 'Armor All Vlažne maramice za staklo 20/1',
        'url': 'https://www.konzum.hr/web/products/maramice-vlazne-20-1'},
    ...
]
```

# Documentation

See the [API documentation](https://jcgoran.github.io/shop-scraper-hr).
