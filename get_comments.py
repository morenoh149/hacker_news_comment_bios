#!/usr/bin/env python3

"""
Usage:
$ ./get_comments.py 35769529

This script downloads all comments in a hackernews thread
by paginating through the api one page at a time.
Then it fetches the bio for each user in parallel using httpx.AsyncClient.
The comments and bios are accumulated into a pandas dataframe.
Finally it writes the pandas dataframe to a csv file.

TODO
[*] add type annotations to update_csv;
[*] move the search_by_date thing into a separate function;
[*] automate the verification of the csv
[*] docstring that you can access with ./get_comments.py --help
[*] put it in a repo with a CI pipeline checking running linters (say flake8)
[ ] make get_comments async
[ ] ci that checks typing (mypy)

This project is licensed under the terms of the MIT license.
"""

import argparse
import asyncio
import csv
import datetime
import io
import time
import os
import urllib.parse

import httpx
import html2text
import pandas as pd

# useful threads to test with
# STORY_ID = "35759449"
# STORY_ID = "35769529"
BASE_URL: str = "https://hn.algolia.com/api/v1"


async def get_bio(username: str, client: httpx.AsyncClient) -> str:
    """
    get_bio async wrapper allowing bios to be fetched in parallel.
    """
    response = await client.get(f"{BASE_URL}/users/{username}")
    data: dict = response.json()
    return data["about"]


def get_comments(story_id: str) -> pd.DataFrame:
    """
    get_comments paginates through a thread in increments of 100
    returns a pandas dataframe

    TODO: after the first request, if there are many pages, load them in
    parallel.
    """
    dataframe: pd.DataFrame = pd.DataFrame()
    page_size: int = 100
    requested_keys: list = [
        "author",
        "created_at_i",
        "objectID",
        "comment_text"]
    headers: dict = {"User-Agent": "curl/7.72.0"}
    api_comment: str = f'{BASE_URL}/search_by_date?'
    page: int = 0
    with httpx.Client(headers=headers, timeout=None) as client:
        while True:
            params: dict = {
                'tags': f'comment,story_{story_id}',
                'hitsPerPage': page_size,
                'page': page}
            url: str = api_comment + urllib.parse.urlencode(params)
            print(f"Fetching page {url}")
            response = client.get(url)
            json: dict = response.json()
            pages: int = json["nbPages"]
            data = pd.DataFrame(json["hits"])[requested_keys]
            dataframe = pd.concat([dataframe, data], ignore_index=True)
            page += 1
            if page >= pages:
                break
    return dataframe


def update_csv(file: io.TextIOWrapper, dataframe: pd.DataFrame) -> None:
    """
    update_csv sanitizes columns in the dataframe and writes to a csv file
    """
    dataframe["comment_text"] = dataframe["comment_text"].map(
        lambda x: html2text.html2text(x).replace(",", "")
    )
    dataframe["created_at"] = dataframe["created_at_i"].map(
        lambda x: datetime.datetime.fromtimestamp(
            int(x), tz=datetime.timezone(datetime.timedelta(hours=-5))
        ).strftime("%Y-%m-%d %H:%M:%S")
    )
    dataframe["bio"] = dataframe["bio"].map(
        lambda x: html2text.html2text(x).replace(",", "")
    )
    ordered_dataframe: pd.DataFrame = dataframe[
        ["author", "created_at", "objectID", "comment_text", "bio"]
    ]
    ordered_dataframe.to_csv(file, encoding="utf-8", index=False)


class InvalidCSVException(Exception):
    "Raised when the csv length does not match the number of bios"


def parser() -> argparse.ArgumentParser:
    """
    parse_args parses the command line argument, story_id
    """
    my_parser = argparse.ArgumentParser(
        prog="Download HackerNews comments",
        description='Download bios from hackernews and store them in a csv')
    my_parser.add_argument('story_id',
                           help='The thread id to download comments for.')
    return my_parser


async def main(my_args: argparse.Namespace) -> None:
    """
    main is the entry point for the script, we time this script.
    """
    t_0 = time.time()

    filename: str = "hackernews_comments.csv"
    if os.path.isfile(filename):
        os.remove(filename)

    dataframe: pd.DataFrame = get_comments(my_args.story_id)
    usernames: pd.Series = dataframe['author']

    print(f'Fetching {len(usernames)} bios')
    headers: dict = {"User-Agent": "curl/7.72.0"}
    async with httpx.AsyncClient(headers=headers, timeout=None) as client:
        tasks: list = [get_bio(user, client) for user in usernames]
        bios = await asyncio.gather(*tasks)

    dataframe['bio'] = bios

    with open(filename, "a", encoding='utf-8') as file:
        update_csv(file, dataframe)

    # verify csv file is the same length as the dataframe plus the header
    with open('hackernews_comments.csv', encoding="utf-8") as file:
        csv_num_lines = sum(1 for i in csv.reader(file))
        if csv_num_lines != (len(dataframe) + 1):
            raise InvalidCSVException("csv file is not the correct length",
                                      len(dataframe),
                                      csv_num_lines)

    print(f"Total time: {time.time() - t_0:.3} seconds")

if __name__ == "__main__":
    args = parser().parse_args()
    asyncio.run(main(args))
