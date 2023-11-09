# This doesn't really belong in this bot but meh. Looks up twitter posts on
# fxtwitter to make them embed properly again.
import re
import discord
import httpx
from bs4 import BeautifulSoup


pattern = re.compile(
    r"<?https?://(?:www\.)?(?:twitter|x)\.com/([\w_]+/status/\d+)(?:\?\S+)?>?"
)
FX_TWITTER_URL = "https://fxtwitter.com"


def register_bot_for_tweet_fixing(client):
    # Register our on_message handler.
    @client.event
    async def on_message(message):
        if message.author.bot or not message.content or not message.channel:
            return

        await on_message_handler(message)


async def on_message_handler(message):
    links = get_fx_twitter_links_from_message(message.content)
    if len(links) < 1:
        return

    print(f"Handling twitter message: {message.content}")

    # Only handle the first link for now.
    async with httpx.AsyncClient() as client:
        r = await client.get(links[0])
        embed = parse_embed_from_fx_twitter_page(r.text)

        print(f"+ Replying with embed")
        await message.reply(embeds=[embed])


def parse_embed_from_fx_twitter_page(page_body) -> discord.Embed:
    embed = discord.Embed()

    soup = BeautifulSoup(page_body, features="html.parser")
    title = soup.find("meta", {"property": "og:title", "content": True})
    if title is not None:
        embed.title = title["content"]

    description = soup.find("meta", {"property": "og:description", "content": True})
    if description is not None:
        embed.description = description["content"]

    url = soup.find("meta", {"property": "og:url", "content": True})
    if url is not None:
        embed.url = url["content"]

    color = soup.find("meta", {"property": "theme-color", "content": True})
    if color is not None:
        color = int(color["content"].replace("#", ""), 16)
        embed.color = color

    image = soup.find("meta", {"property": "og:image", "content": True})
    if image is not None:
        embed.set_image(url=image["content"])

    return embed


def get_fx_twitter_links_from_message(message_content):
    matches = [
        match
        for match in pattern.finditer(message_content)
        if match[0][0] != "<" or match[0][-1] != ">"
    ]
    return [f"{FX_TWITTER_URL}/{match[1]}" for match in matches]
