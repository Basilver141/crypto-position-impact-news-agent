"""
Sends a notification message to your Telegram via your bot.
"""

import requests


def send_telegram_message(bot_token: str, chat_id: str, text: str):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload, timeout=10)
    if response.status_code != 200:
        print(f"[notifier] Failed to send Telegram message: {response.text}")
    return response.ok