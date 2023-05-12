import httpx

url = f"https://hn.algolia.com/api/v1/users/morenoh149"
response = httpx.get(url, headers={"User-Agent":"curl/7.72.0"})
data = response.json()
print(data)