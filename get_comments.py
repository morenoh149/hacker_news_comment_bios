#!/usr/bin/env python3

"""
Usage:
$ ./get_comments.py 35769529

This script downloads all comments in a hackernews thread
by paginating through the api one page at a time.
Then it fetches the bio for each user in parallel using httpx.AsyncClient.
The comments and bios are accumulated into a pandas dataframe.
Finally it writes the pandas dataframe to a csv file.

This project is licensed under the terms of the MIT license.
"""

import argparse
import asyncio
import csv
import datetime
import io
import time
import os

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
    get_comments paginates through a thread in increments of 100 and returns a pandas dataframe
    TODO: after the first request, if there are many pages, load them in parallel.
    """
    df: pd.DataFrame = pd.DataFrame()
    pageSize: int = 100
    requested_keys: list = ["author", "created_at_i", "objectID", "comment_text"]
    headers: dict = {"User-Agent": "curl/7.72.0"}
    page: int = 0
    with httpx.Client(headers=headers, timeout=None) as client:
        while True:
            url: str = f"{BASE_URL}/search_by_date?tags=comment,story_{story_id}&hitsPerPage={pageSize}&page={page}"
            print(f"Fetching page {url}")
            response = client.get(url)
            json: dict = response.json()
            pages: int = json["nbPages"]
            last: int = json["nbHits"] < pageSize
            data = pd.DataFrame(json["hits"])[requested_keys]
            df = pd.concat([df, data], ignore_index=True)
            page += 1
            if page >= pages:
                break
    return df


def update_csv(file: io.TextIOWrapper, df: pd.DataFrame) -> None:
    """
    update_csv sanitizes columns in the dataframe and writes them out to a csv file
    """
    df["comment_text"] = df["comment_text"].map(
        lambda x: html2text.html2text(x).replace(",", "")
    )
    df["created_at"] = df["created_at_i"].map(
        lambda x: datetime.datetime.fromtimestamp(
            int(x), tz=datetime.timezone(datetime.timedelta(hours=-5))
        ).strftime("%Y-%m-%d %H:%M:%S")
    )
    df["bio"] = df["bio"].map(
        lambda x: html2text.html2text(x).replace(",", "")
    )
    ordered_df: pd.DataFrame = df[["author", "created_at", "objectID", "comment_text", "bio"]]
    ordered_df.to_csv(file, encoding="utf-8", index=False)


def parse_args() -> argparse.Namespace:
    """
    parse_args parses the command line argument, story_id
    """
    parser = argparse.ArgumentParser(
        prog="Download HackerNews comments",
        description='Download bios from hackernews and stores them in a csv')
    parser.add_argument('story_id', help='The thread id to download comments from.')
    return parser.parse_args()


async def main() -> None:
    t0 = time.time()

    args: argparse.Namespace = parse_args()

    filename: str = "hackernews_comments.csv"
    if os.path.isfile(filename):
        os.remove(filename)

    df: pd.DataFrame = get_comments(args.story_id)
    usernames: pd.Series = df['author']

    print(f'Fetching {len(usernames)} bios')
    headers: dict = {"User-Agent": "curl/7.72.0"}
    async with httpx.AsyncClient(headers=headers, timeout=None) as client:
        tasks: list = [get_bio(user, client) for user in usernames]
        bios = await asyncio.gather(*tasks)

    df['bio'] = bios

    with open(filename, "a") as file:
        update_csv(file, df)

    # verify csv file is the same length as the dataframe plus the header
    csv_num_lines = sum(1 for i in csv.reader(open('hackernews_comments.csv')))
    if csv_num_lines != (len(df) + 1):
        raise Exception("csv file is not the same length as the dataframe", len(df), csv_num_lines)

    print(f"Total time: {time.time() - t0:.3} seconds")

asyncio.run(main())

"""
TODO
[*] add type annotations to update_csv;
[*] move the search_by_date thing into a separate function;
[ ] make it get_comments async;
[*] automate the verification of the csv
[*] docstring that you can access with myscript --help is a nice touch too
[*] put it in a repo with a CI pipeline checking running linters (say flake8)
[ ] ci that checks typing (mypy)
"""
