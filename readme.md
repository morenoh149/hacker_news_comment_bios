# Download Hacker News Comment Bios

This a tool for getting leads from [HackerNews](https://news.ycombinator.com/) threads.
Often you want to reach
out to people that have participated in a conversation. With this tool you get
a csv of an entire thread along with the About info for the commentor.
This way we can read through a thread and pick out the commentor's email
if they have it in their bio. This tool uses the algolia api for hn.

## Running

Written for python 3.11 and pipenv.

`pipenv install`

`python get_comments.py`

You'll have a `hacker_news_comments.csv` file created locally.

## Other resources

1. Inspired by https://github.com/jaredsohn/hacker-news-download-all-comments
1. algolia api https://hn.algolia.com/api
1. official hn api https://github.com/HackerNews/API#users
1. https://github.com/minimaxir/get-all-hacker-news-submissions-comments
1. https://github.com/itielshwartz/asyncio-hn
