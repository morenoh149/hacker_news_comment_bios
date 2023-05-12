import time

import httpx

t0 = time.time()

usernames = [
"author",
"abtinf",
"TheCoelacanth",
"tomcam",
"chauhankiran",
"ulizzle",
"ulizzle",
"ulizzle",
"cratermoon",
"Aeolun",
"ulizzle",
"firexcy",
"kazinator",
"blacksoil",
"lucakiebel",
"ozim",
"tomcam",
"jstummbillig",
"tomcam",
"johnchristopher",
"Tade0",
"lallysingh",
"paulddraper",
"WilTimSon",
"gumby",
"kristopolous",
"zemo",
"aschearer",
"why-el",
"Osiris",
"mdaniel",
"ianbutler",
"vinaypai",
"samtho",
"chazeon",
"taeric",
"yellowapple",
"Kye",
]

headers = {"User-Agent": "curl/7.72.0"}
with httpx.Client(headers=headers, timeout=None) as client:
    for username in usernames:
        url = f"https://hn.algolia.com/api/v1/users/{username}"
        response = client.get(url)
        data = response.json()
        print('.')

t1 = time.time()
total = t1-t0
print(f"Total time: {total} seconds") # 5.7 seconds sync