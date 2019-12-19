import requests

from presqt.targets.github.utilities import get_page_total


def github_paginated_data(token):
    """
    For the given user, find and return all repo data.

    Parameters
    ----------
    token : str
        The user's GitHub token.

    Returns
    -------
    List of all paginated data.
    """
    base_url = "https://api.github.com/user/repos?access_token={}".format(token)
    data = requests.get(base_url).json()
    page_total = get_page_total(token)
    # We want to start building urls from page 2 as we already have the data from page 1.
    page_count = 2
    while page_count <= page_total:
        next_url = "https://api.github.com/user/repos?page={}&access_token={}".format(page_count,
                                                                                      token)
        next_data = requests.get(next_url).json()
        data.extend(next_data)
        page_count += 1

    return data