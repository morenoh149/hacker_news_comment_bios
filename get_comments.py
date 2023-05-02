import requests
import json
import datetime
import time
import pandas as pd
import os
from pandas import DataFrame
import html2text

STORY_ID = "35759449"
# STORY_ID = "35769529"
filename = "hacker_news_comments.csv"


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


if os.path.isfile(filename):
    os.remove(filename)

df = DataFrame()
hitsPerPage = 100
requested_keys = ["author", "created_at_i", "objectID", "comment_text"]

page = 0

"""
Build dataframe of comments.
You can verify the csv has all the comments by running

`python -c "import csv; print(sum(1 for i in csv.reader(open('hacker_news_comments.csv'))))"`

and make sure the count matches the `nbHits` value from the api.
"""
while True:
    with open(filename, "a") as file:
        try:
            url = f"https://hn.algolia.com/api/v1/search_by_date?tags=comment,story_{STORY_ID}&hitsPerPage={hitsPerPage}&page={page}"
            response = requests.get(url)
            data = response.json()
            pages = data["nbPages"]
            last = data["nbHits"] < hitsPerPage
            data = DataFrame(data["hits"])[requested_keys]
            print(url)
            df = pd.concat([df, data], ignore_index=True)
            time.sleep(1)
            page += 1
            if page >= pages:
                break

        except Exception as e:
            print(e)

"""
Add user bios to dataframe.
This could be parallelized with more work.
"""
bio_counter = 0
def user_bio(row):
    username = row['author']
    url = f"https://hn.algolia.com/api/v1/users/{username}"
    global bio_counter
    bio_counter += 1
    if (bio_counter % 10 == 0):
        print(f'Fetch {bio_counter}. Getting bio for {username}.')
    response = requests.get(url)
    data = response.json()
    return data['about']
df['bio'] = df.apply(user_bio, axis=1)
with open(filename, "a") as file:
    update_csv(file, df)