"""
Fetches headlines from reputable crypto news RSS feeds and matches them
against a watchlist of assets using simple keyword matching.
"""

import feedparser

NEWS_FEEDS = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "The Block": "https://www.theblock.co/rss.xml",
}

# Keywords that map a headline to an asset. Extend these lists as needed.
ASSET_KEYWORDS = {
    "BTC": ["bitcoin", "btc"],
    "ETH": ["ethereum", "eth", "ether"],
    "BNB": ["bnb", "binance coin", "binance chain"],
}


def fetch_all_headlines():
    """Return a list of {title, link, source, summary} across all feeds."""
    headlines = []
    for source, url in NEWS_FEEDS.items():
        try:
            parsed = feedparser.parse(url)
        except Exception as e:
            print(f"[news_feed] Failed to fetch {source}: {e}")
            continue

        for entry in parsed.entries:
            headlines.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "source": source,
            })
    return headlines


def match_headline_to_assets(headline: dict, watched_assets: list[str]):
    """Return list of asset tickers this headline mentions, based on keywords."""
    text = f"{headline['title']} {headline.get('summary', '')}".lower()
    matches = []
    for asset in watched_assets:
        keywords = ASSET_KEYWORDS.get(asset, [asset.lower()])
        if any(kw in text for kw in keywords):
            matches.append(asset)
    return matches