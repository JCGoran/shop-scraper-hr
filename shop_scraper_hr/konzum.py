"""
Utilities for scraping categories and prices from konzum.hr
"""

from __future__ import annotations

import concurrent.futures
from typing import Any

import requests
from bs4 import BeautifulSoup

from shop_scraper_hr.common import get_category_urls_generic, parse_price_string

MAIN_URL = "https://www.konzum.hr"


def get_category_urls(**kwargs):
    return get_category_urls_generic(
        MAIN_URL,
        prefix="/web/t/kategorije/",
        **kwargs,
    )


def parse_item(item) -> dict[str, Any]:
    """
    Parse a given item and return a dictionary that maps to its metadata.

    Returns
    -------
    result : dict
        the dictionary with at least the keys ``url``, ``title``, and
        ``price_data``
    """
    url = MAIN_URL + item.find(class_="product-default__title").find("a")["href"]
    title = item.find(class_="product-default__title").text.strip()
    price_data = item.find(
        "div",
        class_="product-default__prices js-product-price-data",
    )
    price_integer_part = int(price_data.find("span", class_="price--kn").text.strip())
    price_fractional_part = int(
        price_data.find("span", class_="price--li").text.strip()
    )
    currency_per_unit_quantity = price_data.find(
        "small", class_="price--c"
    ).text.strip()
    try:
        price_data = parse_price_string(
            price_data.find("div", class_=None).find("strong").text.strip()
        )
    except AttributeError:
        price_data = None

    loc = locals()

    return {
        key: loc[key]
        for key in [
            "price_fractional_part",
            "price_integer_part",
            "currency_per_unit_quantity",
            "price_data",
            "url",
            "title",
        ]
    }


def parse_page(content: str) -> list[dict[str, Any]]:
    """
    Parse a single page of results from konzum.hr and return all items on it.
    """
    soup = BeautifulSoup(content, "html.parser")
    items = soup.find_all("div", class_="product-wrapper")

    return [parse_item(item) for item in items]


def get_prices(
    category_url: str,
    max_workers: int = 1,
    **kwargs,
) -> list[dict[str, Any]]:
    """
    Get the prices of all of the items in a particular category.
    """
    response = requests.get(category_url, **kwargs)
    soup = BeautifulSoup(response.text, "html.parser")
    result = parse_page(response.text)

    # multiple pages found
    if soup.find("ul", class_="pagination"):
        pages = max(
            int(item.text.strip()) if item.text.strip().isnumeric() else 0
            for item in soup.find("ul", class_="pagination").find_all("li")
        )
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_results = [
                executor.submit(
                    requests.get,
                    f"{category_url}?page={page}",
                    **kwargs,
                )
                for page in range(1, pages + 1)
            ]

            for future_result in concurrent.futures.as_completed(future_results):
                result.extend(parse_page(future_result.result().text))

    return result


def get_all_prices(max_workers: int = 1, **kwargs) -> list[dict[str, Any]]:
    """
    Get prices for all items from konzum.hr

    Parameters
    ----------
    max_workers : int, optional
        the number of workers for the concurrent execution (using
        ``concurrent.futures.ThreadPoolExecutor``) (default: 1)

    **kwargs
        any keyword args passed to ``requests.get``

    Returns
    -------
    result
        the list of dictionaries with prices (see ``parse_item`` for details of
        items in the dictionary)
    """
    categories = get_category_urls(**kwargs)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_results = [
            executor.submit(
                get_prices,
                category,
                **kwargs,
            )
            for category in categories
        ]

    return [
        item
        for future_result in concurrent.futures.as_completed(future_results)
        for item in future_result.result()
    ]
