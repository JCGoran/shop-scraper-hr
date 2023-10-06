"""
Module containing utilities for scraping categories and prices from tommy.hr
"""
from __future__ import annotations

import concurrent.futures
import unicodedata
from typing import Any

import requests
from bs4 import BeautifulSoup

from shop_scraper_hr.common import get_category_urls_generic, parse_price_string

MAIN_URL = "https://www.tommy.hr"


def get_category_urls(**kwargs) -> list[str]:
    """
    Return a list of URLs to all categories.
    """
    return get_category_urls_generic(
        MAIN_URL,
        prefix="/kategorije/",
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
    url = MAIN_URL + item.find("h3").find("a")["href"]
    title = item.find("h3").text.strip()
    # for some reason, there are two price containers, one inside the other
    # the site also uses &nbsp; so I use `normalize` here to replace it with a
    # regular whitespace
    price_data = parse_price_string(
        unicodedata.normalize(
            "NFKD", item.find("span").find("span").previous_sibling.text.strip()
        )
    )
    loc = locals()

    return {
        key: loc[key]
        for key in [
            "price_data",
            "url",
            "title",
        ]
    }


def get_prices(url: str, **kwargs) -> list[dict[str, Any]]:
    """
    Get the prices of all of the items in a particular category.

    Parameters
    ----------
    url : str
        the URL of a category from which to fetch the prices
    """
    response = requests.get(url, **kwargs)
    content = BeautifulSoup(response.text, "html.parser")
    items = content.find_all(class_="w-full h-full flex flex-col my-4 leading-normal")

    return [parse_item(item) for item in items]


def get_all_prices(max_workers: int = 1, **kwargs):
    """
    Get prices for all items from tommy.hr

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
