from datetime import datetime, timezone
import requests

ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

def get_hours_until_next_tipoff() -> float | None:
    """
    Returns hours until the next NBA tip-off today.
    Returns None if no games are scheduled today.
    """
    try:
        resp = requests.get(ESPN_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"ESPN check failed: {e}")
        return None  # if ESPN is down, default to allowing a poll

    now = datetime.now(timezone.utc)
    upcoming = []

    for event in data.get("events", []):
        status = event["status"]["type"]["name"]
        if status in ("STATUS_FINAL", "STATUS_IN_PROGRESS"):
            continue  # skip finished or live games
        tip_str = event.get("date")  # ISO format: "2025-03-18T23:30Z"
        if tip_str:
            tip = datetime.fromisoformat(tip_str.replace("Z", "+00:00"))
            hours_away = (tip - now).total_seconds() / 3600
            if hours_away > 0:
                upcoming.append(hours_away)

    return min(upcoming) if upcoming else None

def should_poll_odds() -> bool:
    """
    Decision layer: should we spend an Odds API credit right now?
    """
    hours = get_hours_until_next_tipoff()

    if hours is None:
        print("No games today. Skipping Odds API poll.")
        return False

    if hours > 6:
        print(f"Next tip-off in {hours:.1f}h — too early, skipping.")
        return False

    if hours > 2:
        # Quiet window: poll roughly once per hour on average
        import random
        roll = random.random()
        fires = roll < 0.5   # 50% chance per 30-min tick = ~once/hr
        print(f"Next tip-off in {hours:.1f}h — {'polling' if fires else 'skipping'} (p=0.5)")
        return fires

    print(f"Next tip-off in {hours:.1f}h — within hot window, polling.")
    return True