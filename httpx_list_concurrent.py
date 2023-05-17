"""
proof of concept, get all bios in parallel using asyncio
"""

import asyncio
import time

import httpx


BASE_URL = "https://hn.algolia.com/api/v1/users"

async def get_bio(username: str, client: httpx.AsyncClient) -> str:
    """
    get_bio async wrapper allowing bios to be fetched in parallel.
    """
    response = await client.get(f"{BASE_URL}/{username}")
    print(".")
    data = response.json()
    return data["about"]


async def main() -> None:
    """
    main async function
    """
    t_0 = time.time()
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
    async with httpx.AsyncClient(headers=headers, timeout=None) as client:
        tasks = [get_bio(user, client) for user in usernames]
        bios = await asyncio.gather(*tasks)
    print(dict(zip(usernames, bios)))
    print(f"Total time: {time.time() - t_0:.3} seconds")

asyncio.run(main())
