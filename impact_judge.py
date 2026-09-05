"""
Rule-based impact judgment — NO paid API required.
"""

HIGH_IMPACT_KEYWORDS = [
    "hack", "hacked", "exploit", "exploited", "breach", "stolen", "theft",
    "delist", "delisting", "ban", "banned", "lawsuit", "sec charges",
    "sec sues", "indictment", "fraud", "collapse", "insolvent", "insolvency",
    "bankrupt", "bankruptcy", "depeg", "depegged", "halt", "halted",
    "frozen", "freeze", "rug pull", "outage",
]

MEDIUM_IMPACT_KEYWORDS = [
    "regulation", "regulatory", "investigation", "probe", "fine", "fined",
    "etf approval", "etf rejected", "etf decision", "partnership",
    "listing", "upgrade", "fork", "vulnerability", "warning", "downgrade",
    "sell-off", "selloff", "liquidation", "liquidated", "outflow", "inflow",
]

LOW_SIGNAL_KEYWORDS = [
    "price prediction", "analysis", "opinion", "explainer", "how to",
    "beginner", "guide",
]


def judge_impact(asset: str, headline: str, summary: str, position_context: str) -> dict:
    text = f"{headline} {summary}".lower()
    matched_high = [kw for kw in HIGH_IMPACT_KEYWORDS if kw in text]
    matched_medium = [kw for kw in MEDIUM_IMPACT_KEYWORDS if kw in text]
    matched_low = [kw for kw in LOW_SIGNAL_KEYWORDS if kw in text]
    score = len(matched_high) * 3 + len(matched_medium) * 1 - len(matched_low) * 2
    impactful = score >= 2
    if matched_high:
        reason = f"Mentions high-risk term(s): {', '.join(matched_high[:3])}."
    elif matched_medium:
        reason = f"Mentions notable term(s): {', '.join(matched_medium[:3])}."
    else:
        reason = "No strong impact keywords detected."
    return {"impactful": impactful, "reason": reason, "score": score}