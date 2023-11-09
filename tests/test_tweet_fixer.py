from events_bot import tweet_fixer


def test_gets_correct_links_from_message():
    matches = tweet_fixer.get_fx_twitter_links_from_message(
        """\
        https://twitter.com/dril/status/384408932061417472?lang=en
        https://x.com/craigus12/status/384411321099640833
                """
    )

    assert matches == [
        "https://fxtwitter.com/dril/status/384408932061417472",
        "https://fxtwitter.com/craigus12/status/384411321099640833",
    ]


FX_TWITTER_RESPONSE = """\
<!DOCTYPE html><html lang="en"><!--

   █████ ▐█▌       ███████████                              ███
 ███      █            ███                                  ███
███                    ███                                  ███
███      ███  ███  ███ ███  ███  ███  ███  ██████   ██████  ██████
███████▌ ███   ▐█▌▐█▌  ███  ███  ███  ███ ▐█▌  ▐█▌ ▐█▌  ▐█▌ ███
███      ███    ▐██▌   ███  ███  ███  ███ ████████ ████████ ███
███      ███   ▐█▌▐█▌  ███  ▐██▌ ███ ▐██▌ ▐█▌      ▐█▌      ▐██▌
███      ███  ███  ███ ███   ▐█████████▌    ▐████    ▐████    ▐████
███
███   A better way to embed Tweets on Discord, Telegram, and more.
███   Worker build fixtweet-main-3e4e0ea-2023-11-08T23:42:36

--><head><link rel="canonical" href="https://twitter.com/dril/status/384408932061417472"/><meta property="og:url" content="https://twitter.com/dril/status/384408932061417472"/><meta property="theme-color" content="#00a8fc"/><meta property="twitter:site" content="@dril"/><meta property="twitter:creator" content="@dril"/><meta property="twitter:title" content="wint (@dril)"/><meta http-equiv="refresh" content="0;url=https://twitter.com/dril/status/384408932061417472"/><meta property="og:image" content="https://pbs.twimg.com/profile_images/1510917391533830145/XW-zSFDJ_200x200.jpg"/><meta property="twitter:image" content="0"/><meta property="og:title" content="wint (@dril)"/><meta property="og:description" content="Food $200
Data $150
Rent $800
Candles $3,600
Utility $150
someone who is good at the economy please help me budget this. my family is dying"/><meta property="og:site_name" content="FixTweet / FixupX"/><meta property="twitter:card" content="undefined"/><link rel="alternate" href="https://fxtwitter.com/owoembed?text=969%20%F0%9F%92%AC%20%20%20%2056%2C143%20%F0%9F%94%81%20%20%20%20126%2C750%20%E2%9D%A4%EF%B8%8F&status=384408932061417472&author=dril" type="application/json+oembed" title="wint"></head><body></body></html>
"""


def test_parses_into_embed_correctly():
    embed = tweet_fixer.parse_embed_from_fx_twitter_page(FX_TWITTER_RESPONSE)
    assert embed.title == "wint (@dril)"
    assert (
        embed.description
        == """\
Food $200
Data $150
Rent $800
Candles $3,600
Utility $150
someone who is good at the economy please help me budget this. my family is dying"""
    )
    assert embed.url == "https://twitter.com/dril/status/384408932061417472"
    assert embed.color.value == 0x00A8FC
