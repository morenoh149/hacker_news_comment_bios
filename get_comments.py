import argparse
import asyncio
import datetime
import time
import os

import httpx
import html2text
import pandas as pd


# STORY_ID = "35759449"
# STORY_ID = "35769529"
BASE_URL = "https://hn.algolia.com/api/v1"


async def get_bio(username: str, client: httpx.AsyncClient) -> str:
    response = await client.get(f"{BASE_URL}/users/{username}")
    data = response.json()
    return data["about"]

def update_csv(file, df):
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
    ordered_df = df[["author", "created_at", "objectID", "comment_text", "bio"]]
    ordered_df.to_csv(file, encoding="utf-8", index=False)

def parse_args():
    parser = argparse.ArgumentParser(description='Download bios from hackernews.')
    parser.add_argument('story_id', help='The thread id to download comments from.')
    return parser.parse_args()


"""
This script first finds all comments in a thread by paginating through the api one page at a time.
Then it fetches the bio for each user in parallel using httpx.AsyncClient.
Finally it writes the results from the pandas dataframe into a csv file.


You can verify the csv has all the comments by running

`python -c "import csv; print(sum(1 for i in csv.reader(open('hackernews_comments.csv'))))"`

and make sure the count matches the `nbHits` value from the api.
"""
async def main() -> None:
    t0 = time.time()

    args = parse_args()
    STORY_ID = args.story_id

    filename = "hackernews_comments.csv"
    if os.path.isfile(filename):
        os.remove(filename)

    df = pd.DataFrame()
    pageSize = 100
    requested_keys = ["author", "created_at_i", "objectID", "comment_text"]
    headers = {"User-Agent": "curl/7.72.0"}
    page = 0
    with httpx.Client(headers=headers, timeout=None) as client:
        while True:
            url = f"{BASE_URL}/search_by_date?tags=comment,story_{STORY_ID}&hitsPerPage={pageSize}&page={page}"
            response = client.get(url)
            data = response.json()
            pages = data["nbPages"]
            last = data["nbHits"] < pageSize
            data = pd.DataFrame(data["hits"])[requested_keys]
            print(f"Fetching page {url}")
            df = pd.concat([df, data], ignore_index=True)
            page += 1
            if page >= pages:
                break
    usernames = df['author']

    print(f'Fetching {len(usernames)} bios')
    async with httpx.AsyncClient(headers=headers, timeout=None) as client:
        tasks = [get_bio(user, client) for user in usernames]
        bios = await asyncio.gather(*tasks)

    df['bio'] = bios

    with open(filename, "a") as file:
        update_csv(file, df)
    print(f"Total time: {time.time() - t0:.3} seconds")

asyncio.run(main())