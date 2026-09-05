"""
Crypto Position-Impact News Agent
Built for the Binance Agent OS Mini Hackathon (Track A).
Read-only: never places trades, never touches withdrawals.
100% free to run.
"""

import os
import time
import json
from dotenv import load_dotenv

from binance_client import BinanceReadOnlyClient
from news_feed import fetch_all_headlines, match_headline_to_assets
from impact_judge import judge_impact
from notifier import send_telegram_message

SEEN_FILE = "seen_headlines.json"


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen(seen: set):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def build_position_context(holdings: dict, asset: str) -> str:
    info = holdings.get(asset, {})
    balance = info.get("balance", {})
    orders = info.get("open_orders", [])
    lines = [
        f"Balance: {balance.get('free', 0)} free, {balance.get('locked', 0)} locked {asset}",
        f"Open orders: {len(orders)}",
    ]
    for o in orders[:5]:
        lines.append(f"  - {o.get('side')} {o.get('origQty')} @ {o.get('price')} ({o.get('type')})")
    return "\n".join(lines)


def main():
    load_dotenv()
    binance_key = os.environ["BINANCE_API_KEY"]
    binance_secret = os.environ["BINANCE_API_SECRET"]
    telegram_token = os.environ["TELEGRAM_BOT_TOKEN"]
    telegram_chat_id = os.environ["TELEGRAM_CHAT_ID"]
    watched_assets = [a.strip().upper() for a in os.environ.get("WATCHED_ASSETS", "BTC,ETH,BNB").split(",")]
    poll_interval = int(os.environ.get("POLL_INTERVAL_SECONDS", "300"))

    binance_client = BinanceReadOnlyClient(binance_key, binance_secret)
    seen_headlines = load_seen()

    print(f"[agent] Watching {watched_assets}. Polling every {poll_interval}s. Ctrl+C to stop.")

    while True:
        try:
            holdings = binance_client.get_holdings_and_orders_for_assets(watched_assets)
            headlines = fetch_all_headlines()
            new_count = 0
            for headline in headlines:
                key = headline["link"] or headline["title"]
                if key in seen_headlines:
                    continue
                seen_headlines.add(key)
                new_count += 1
                matched_assets = match_headline_to_assets(headline, watched_assets)
                if not matched_assets:
                    continue
                for asset in matched_assets:
                    context = build_position_context(holdings, asset)
                    verdict = judge_impact(asset, headline["title"], headline.get("summary", ""), context)
                    if verdict["impactful"]:
                        message = (
                            f"*Possible impact on your {asset} position*\n\n"
                            f"{headline['title']}\n"
                            f"Source: {headline['source']}\n\n"
                            f"Why it matters: {verdict['reason']}\n\n"
                            f"{headline['link']}"
                        )
                        send_telegram_message(telegram_token, telegram_chat_id, message)
                        print(f"[agent] Sent alert for {asset}: {headline['title']}")
            save_seen(seen_headlines)
            print(f"[agent] Checked {len(headlines)} headlines, {new_count} new, sleeping {poll_interval}s.")
        except Exception as e:
            print(f"[agent] Error in main loop: {e}")
        time.sleep(poll_interval)


if __name__ == "__main__":
    main()