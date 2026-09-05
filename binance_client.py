"""
Read-only Binance client.

Uses a Binance API key/secret with "Enable Reading" permission ONLY.
This code never places trades and never touches withdrawals — it only
reads account balances and open orders, which is all Track A's demo needs.
"""

import time
import hmac
import hashlib
import os
import requests
from urllib.parse import urlencode

BASE_URL = "https://api.binance.com"


class BinanceReadOnlyClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

    def _signed_request(self, path: str, params: dict = None):
        params = params or {}
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        query_string += f"&signature={signature}"

        headers = {"X-MBX-APIKEY": self.api_key}
        url = f"{BASE_URL}{path}?{query_string}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_balances(self, min_balance: float = 0.0):
        """Return list of {asset, free, locked} for non-zero balances."""
        data = self._signed_request("/api/v3/account")
        balances = []
        for b in data.get("balances", []):
            free = float(b["free"])
            locked = float(b["locked"])
            total = free + locked
            if total > min_balance:
                balances.append({"asset": b["asset"], "free": free, "locked": locked})
        return balances

    def get_open_orders(self, symbol: str = None):
        """Return open orders, optionally filtered to a single symbol e.g. 'BTCUSDT'."""
        params = {"symbol": symbol} if symbol else {}
        return self._signed_request("/api/v3/openOrders", params)

    def get_holdings_and_orders_for_assets(self, assets: list[str]):
        """
        Convenience method: for a list of base assets like ['BTC', 'ETH', 'BNB'],
        return their balances and any open orders on their USDT pairs.
        """
        if os.environ.get("DEMO_MODE", "").strip().lower() == "true":
            demo_balances = {
                "BTC": {"asset": "BTC", "free": 0.05, "locked": 0.0},
                "ETH": {"asset": "ETH", "free": 1.2, "locked": 0.0},
                "BNB": {"asset": "BNB", "free": 10.0, "locked": 0.0},
            }
            return {
                asset: {
                    "balance": demo_balances.get(
                        asset,
                        {"asset": asset, "free": 0.0, "locked": 0.0},
                    ),
                    "open_orders": [],
                }
                for asset in assets
            }

        balances = self.get_balances()
        balances_by_asset = {b["asset"]: b for b in balances}

        result = {}
        for asset in assets:
            symbol = f"{asset}USDT"
            try:
                orders = self.get_open_orders(symbol)
            except requests.HTTPError:
                orders = []
            result[asset] = {
                "balance": balances_by_asset.get(asset, {"asset": asset, "free": 0.0, "locked": 0.0}),
                "open_orders": orders,
            }
        return result