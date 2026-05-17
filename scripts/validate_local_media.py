#!/usr/bin/env python3
"""Quick validation: test Track A site: queries for specific company+outlet combos."""
import feedparser
import urllib.parse


def rss_url(query: str) -> str:
    q = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


def test_query(label: str, company: str, site: str, max_show: int = 5) -> int:
    query = f'"{company}" site:{site}'
    url = rss_url(query)
    feed = feedparser.parse(url)
    entries = getattr(feed, "entries", [])
    print(f"\n=== {label} | query: {query} ===")
    print(f"Found {len(entries)} entries")
    for e in entries[:max_show]:
        pub = getattr(e, "published", "no-date")
        title = getattr(e, "title", "")
        print(f"  [{pub}] {title}")
    return len(entries)


if __name__ == "__main__":
    results = {}

    # Primary validation: KSAT (San Antonio) + Waymo - the flood recall story
    results["KSAT+Waymo"] = test_query("KSAT San Antonio + Waymo", "Waymo", "ksat.com")

    # KXAN Austin + Waymo
    results["KXAN+Waymo"] = test_query("KXAN Austin + Waymo", "Waymo", "kxan.com")

    # AJC Atlanta + Waymo (high volume expected)
    results["AJC+Waymo"] = test_query("AJC Atlanta + Waymo", "Waymo", "ajc.com")

    # Austin Statesman + Tesla (Robotaxi launch coverage)
    results["Statesman+Tesla"] = test_query("Austin Statesman + Tesla", "Tesla", "statesman.com")

    # Dallas Morning News + Aurora
    results["DMN+Aurora"] = test_query("Dallas Morning News + Aurora", "Aurora", "dallasnews.com")

    # Chicago Tribune + Waymo (announced expansion)
    results["ChiTrib+Waymo"] = test_query("Chicago Tribune + Waymo", "Waymo", "chicagotribune.com")

    print("\n\n=== Summary ===")
    for label, count in results.items():
        status = "OK" if count > 0 else "EMPTY"
        print(f"  {status:5s} {label}: {count} entries")
