# Hacker News Comment Bios

![pylint](https://github.com/morenoh149/hacker_news_comment_bios/actions/workflows/pylint.yml/badge.svg)
[![flake8](https://github.com/morenoh149/hacker_news_comment_bios/actions/workflows/flake8.yml/badge.svg)](https://github.com/morenoh149/hacker_news_comment_bios/actions/workflows/flake8.yml)


This is a tool for getting leads from [HackerNews](https://news.ycombinator.com/) threads.
Often you want to reach
out to people that have participated in a conversation. With this tool you get
a csv of an entire thread along with the About info for the commentor.
Because HN bios do not have an email field, users usually put their
email in the about section.

![screenshot](screenshot.png)

## Running

Written for python 3.11 and pipenv.

1. `pipenv install`
1. Find the thread id. it is the last number in the url `https://news.ycombinator.com/item?id=35759449`
1. run `python get_comments.py 35759449`

You'll have a `hackernews_comments.csv` file created locally.

## Other resources

1. Inspired by https://github.com/jaredsohn/hacker-news-download-all-comments
1. algolia api https://hn.algolia.com/api
1. official hn api https://github.com/HackerNews/API#users
1. https://github.com/minimaxir/get-all-hacker-news-submissions-comments
1. https://github.com/itielshwartz/asyncio-hn
