#!/usr/bin/env python3
import argparse
import asyncio
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
    parser = argparse.ArgumentParser(description='Download bios from hackernews.')
    parser.add_argument('story_id', help='The thread id to download comments from.')
    return parser.parse_args()


"""
This script first finds all comments in a thread by paginating through the api one page at a time.
Then it fetches the bio for each user in parallel using httpx.AsyncClient.
Finally it writes the results from the pandas dataframe into a csv file.


You can verify the csv has all the comments by running


and make sure the count matches the `nbHits` value from the api.
"""
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

    """
    verify csv like `python -c "import csv; print(sum(1 for i in csv.reader(open('hackernews_comments.csv'))))"`
    """

    print(f"Total time: {time.time() - t0:.3} seconds")

asyncio.run(main())

"""
TODO
* add type annotations to update_csv;
* move the search_by_date thing into a separate function;
[ ] make it async;
[ ] automate the verification on line 51

Clean up the comments to be more specific "in a thread", what thread? One site supported?
And move the comments to the top.
And toss a license on it.
It looks fine to me as a portfolio piece, you just want to assume that anyone looking at it for portfolio purposes
has limited time and wants to see at a quick glance what it does, so be very clear at the top of the file what it does.
Tossing a license also says "this I have made as a contribution", which is good.

[ ] converting the "this is documentation" comment into a docstring that you can access with myscript --help is a nice touch too

[ ] finish out typing and put it in a repo with a CI pipeline checking the typing and running linters (say flake8) on it
"""