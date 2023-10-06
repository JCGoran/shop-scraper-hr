"""
Module for extracting data from ``konzum.hr``
"""
from __future__ import annotations

import re
from typing import Any

import requests
from bs4 import BeautifulSoup


def remove_parent_strings(data: list[str], /) -> list[str]:
    """
    Remove any strings that are parents of other strings.
    """
    filtered_data = []
    for i, string in enumerate(data):
        is_prefix = False
        for j in range(i + 1, len(data)):
            if data[j].startswith(string):
                is_prefix = True
                break
        if not is_prefix:
            filtered_data.append(string)

    return filtered_data


def get_category_urls_generic(url: str, prefix: str, **kwargs):
    """
    Make a request to an URL and return URLs to all browsable categories.
    """
    response = requests.get(url, **kwargs)
    content = BeautifulSoup(response.text, "html.parser")

    # extract all of the paths (relative URLs) from the page
    all_paths = sorted(
        {
            item.get("href")
            for item in content.find_all(
                "a",
                attrs={"href": lambda x: x and x.startswith(prefix)},
            )
        }
    )

    filtered_paths = remove_parent_strings(all_paths)

    # put the main URL in the front
    filtered_paths = [f"{url}{item}" for item in filtered_paths]

    return filtered_paths


def parse_price_string(s: str, /) -> dict[str, Any]:
    """
    Parses a price string and returns the result as a dictionary.
    If the string cannot be parsed, it returns the original string.
    """
    amount = re.search(r"[0-9]*(\.|,)?[0-9]+", s)
    currency = re.search(r"(€|kn)", s)
    quantity_prefixes = {
        "l": ["m", "d", ""],
        "g": ["k", ""],
        "kom": [""],
    }
    quantity_prefixes_search_list = [
        f"{value}{key}" for key, values in quantity_prefixes.items() for value in values
    ]
    quantity_unit = re.search(rf'({"|".join(quantity_prefixes_search_list)})', s)

    loc = locals()

    return {
        key: getattr(value, "group", lambda *args, **kwargs: None)(0)
        for key, value in loc.items()
        if key not in ["s", "quantity_prefixes", "quantity_prefixes_search_list"]
    }
