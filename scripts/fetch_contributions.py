"""
Scrape kshitisha's public contribution calendar from GitHub.
No token needed — GitHub serves this as public HTML.
"""
import json, re, datetime
from pathlib import Path
import requests
from bs4 import BeautifulSoup

USERNAME = "kshitisha"
URL = f"https://github.com/users/{USERNAME}/contributions"

def fetch():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "X-Requested-With": "XMLHttpRequest",
    }
    resp = requests.get(URL, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    for td in soup.select("td[data-date]"):
        date_str = td["data-date"]
        level = int(td.get("data-level", 0))
        aria = td.get("aria-label", "")
        m = re.search(r"(\d+)\s+contribution", aria)
        count = int(m.group(1)) if m else level
        days.append({"date": date_str, "count": count, "level": level})

    days.sort(key=lambda d: d["date"])

    # Total from page header
    total_el = soup.select_one("h2.f4")
    total_text = total_el.get_text(strip=True) if total_el else ""
    total_match = re.search(r"([\d,]+)\s+contribution", total_text)
    total = int(total_match.group(1).replace(",", "")) if total_match else sum(d["count"] for d in days)

    # Streaks
    counts = [d["count"] for d in days]
    cur_streak = 0
    for c in reversed(counts):
        if c > 0: cur_streak += 1
        else: break
    longest = run = 0
    for c in counts:
        if c > 0:
            run += 1; longest = max(longest, run)
        else:
            run = 0

    best = max(days, key=lambda d: d["count"]) if days else {"date": "N/A", "count": 0}

    out = {
        "username": USERNAME,
        "fetched": datetime.date.today().isoformat(),
        "total": total,
        "best_day": best,
        "current_streak": cur_streak,
        "longest_streak": longest,
        "days": days,
    }
    Path("data").mkdir(exist_ok=True)
    with open("data/contributions.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"Saved {len(days)} days | total={total} | streak={cur_streak}d | longest={longest}d")

if __name__ == "__main__":
    fetch()
