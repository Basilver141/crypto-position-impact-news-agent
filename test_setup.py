"""
Run this FIRST to confirm your API keys and Telegram bot are working.
"""

import os
from dotenv import load_dotenv
from binance_client import BinanceReadOnlyClient
from notifier import send_telegram_message
from news_feed import fetch_all_headlines

load_dotenv()


def test_binance():
    print("\n--- Testing Binance connection ---")
    client = BinanceReadOnlyClient(os.environ["BINANCE_API_KEY"], os.environ["BINANCE_API_SECRET"])
    watched = [a.strip().upper() for a in os.environ.get("WATCHED_ASSETS", "BTC,ETH,BNB").split(",")]
    holdings = client.get_holdings_and_orders_for_assets(watched)
    for asset, info in holdings.items():
        bal = info["balance"]
        print(f"{asset}: free={bal['free']} locked={bal['locked']} open_orders={len(info['open_orders'])}")
    print("Binance connection OK.")


def test_telegram():
    print("\n--- Testing Telegram ---")
    ok = send_telegram_message(
        os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"],
        "Test message from your crypto news agent. If you see this, Telegram is working.",
    )
    print("Telegram message sent OK." if ok else "Telegram message FAILED -- check your token/chat ID.")


def test_news():
    print("\n--- Testing news feeds ---")
    headlines = fetch_all_headlines()
    print(f"Fetched {len(headlines)} headlines total.")
    for h in headlines[:3]:
        print(f" - [{h['source']}] {h['title']}")


if __name__ == "__main__":
    test_binance()
    test_telegram()
    test_news()
    print("\nAll checks complete. If everything above looks right, run: python main.py")