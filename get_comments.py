import requests
import json
import datetime
import time
import pandas as pd
import os
from pandas import DataFrame
import html2text

story_id = '35759449'
filename = 'hacker_news_comments.csv'

def update_csv(file, df):
    df["comment_text"] = df["comment_text"].map(lambda x: html2text.html2text(x).replace(',',''))
    df["created_at"] = df["created_at_i"].map(lambda x: datetime.datetime.fromtimestamp(int(x), tz=datetime.timezone(datetime.timedelta(hours=-5))).strftime('%Y-%m-%d %H:%M:%S'))
    ordered_df = df[["author", "created_at", "objectID", "comment_text"]]
    ordered_df.to_csv(file, encoding='utf-8', index=False)


if os.path.isfile(filename):
    os.remove(filename)

df = DataFrame()
hitsPerPage = 100
requested_keys = ["author", "created_at_i", "objectID", "comment_text"]

page = 0

while True:
    with open(filename, 'a') as file:
        try:
            url = f"https://hn.algolia.com/api/v1/search_by_date?tags=comment,story_{story_id}&hitsPerPage={hitsPerPage}&page={page}"
            response = requests.get(url)
            data = response.json()
            pages = data["nbPages"]
            last = data["nbHits"] < hitsPerPage
            data = DataFrame(data["hits"])[requested_keys]
            print(url)
            df = pd.concat([df, data], ignore_index=True)
            time.sleep(1)
            page += 1
            if (page >= pages):
                update_csv(file, df)
                break

        except Exception as e:
            print(e)