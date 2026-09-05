"""
Demo trigger script for recording the hackathon video.
"""

import os
from dotenv import load_dotenv

from binance_client import BinanceReadOnlyClient
from news_feed import match_headline_to_assets
from impact_judge import judge_impact
from notifier import send_telegram_message

load_dotenv()

DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() == "true"

FAKE_HEADLINES = [
    {
        "title": "Major exchange discloses Bitcoin wallet hack, millions in BTC stolen",
        "summary": "Security researchers confirm a breach affecting hot wallets.",
        "link": "https://example.com/fake-btc-hack-demo",
        "source": "Demo Feed",
    },
    {
        "title": "SEC files lawsuit alleging fraud tied to Ethereum-based project",
        "summary": "Regulators allege violations of securities law.",
        "link": "https://example.com/fake-eth-lawsuit-demo",
        "source": "Demo Feed",
    },
]


def main():
    telegram_token = os.environ["TELEGRAM_BOT_TOKEN"]
    telegram_chat_id = os.environ["TELEGRAM_CHAT_ID"]
    watched_assets = [a.strip().upper() for a in os.environ.get("WATCHED_ASSETS", "BTC,ETH,BNB").split(",")]

    if DEMO_MODE:
        holdings = {
            "BTC": {"balance": {"free": 0.05, "locked": 0}, "open_orders": []},
            "ETH": {"balance": {"free": 1.2, "locked": 0}, "open_orders": []},
            "BNB": {"balance": {"free": 10, "locked": 0}, "open_orders": []},
        }
    else:
        binance_client = BinanceReadOnlyClient(os.environ["BINANCE_API_KEY"], os.environ["BINANCE_API_SECRET"])
        holdings = binance_client.get_holdings_and_orders_for_assets(watched_assets)

    print("Running demo trigger with fake headlines...\n")

    for headline in FAKE_HEADLINES:
        matched_assets = match_headline_to_assets(headline, watched_assets)
        print(f"Headline: {headline['title']}")
        print(f"Matched assets: {matched_assets}")

        for asset in matched_assets:
            verdict = judge_impact(asset, headline["title"], headline["summary"], "")
            print(f"  Verdict for {asset}: {verdict}")

            if verdict["impactful"]:
                message = (
                    f"*Possible impact on your {asset} position*\n\n"
                    f"{headline['title']}\n"
                    f"Source: {headline['source']}\n\n"
                    f"Why it matters: {verdict['reason']}\n\n"
                    f"{headline['link']}"
                )
                sent = send_telegram_message(telegram_token, telegram_chat_id, message)
                print(f"  Telegram alert sent: {sent}")
        print()


if __name__ == "__main__":
    main()