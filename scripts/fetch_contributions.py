#!/usr/bin/env python3
"""
fetch_contributions.py
Scrapes GitHub's public contributions HTML page for a given username,
extracts contribution dates, levels, and counts, and calculates streaks.
Saves the structured result to data/contributions.json.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup

def fetch_contributions(username: str) -> dict:
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch contributions for {username}: HTTP {response.status_code}")
        
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Map tooltips by id
    tooltips = {}
    for tt in soup.find_all("tool-tip"):
        for_id = tt.get("for")
        if for_id:
            tooltips[for_id] = tt.get_text(strip=True)
            
    calendar_days = soup.find_all("td", class_="ContributionCalendar-day")
    if not calendar_days:
        raise RuntimeError("No contribution calendar days found in response.")
        
    days_data = []
    
    for td in calendar_days:
        date_str = td.get("data-date")
        if not date_str:
            continue
            
        level = int(td.get("data-level", 0))
        td_id = td.get("id", "")
        tooltip_text = tooltips.get(td_id, "")
        
        # Parse count from tooltip, e.g. "3 contributions on September 19th." or "No contributions..."
        count = 0
        if "No contributions" in tooltip_text:
            count = 0
        else:
            match = re.search(r"(\d+)\s+contribution", tooltip_text)
            if match:
                count = int(match.group(1))
            elif level > 0:
                # Fallback if text format differs slightly
                count = level
                
        days_data.append({
            "date": date_str,
            "level": level,
            "count": count
        })
        
    # Sort by date
    days_data.sort(key=lambda d: d["date"])
    
    # Calculate streak statistics
    total_contributions = sum(d["count"] for d in days_data)
    active_days = sum(1 for d in days_data if d["count"] > 0)
    
    # Calculate streaks
    longest_streak = 0
    current_streak = 0
    temp_streak = 0
    
    for day in days_data:
        if day["count"] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0
            
    # Calculate current streak ending at latest date
    # If today's count is 0, allow yesterday to continue the streak
    reversed_days = list(reversed(days_data))
    if reversed_days:
        idx = 0
        # If the most recent day is 0, check if yesterday had contributions
        if reversed_days[0]["count"] == 0 and len(reversed_days) > 1 and reversed_days[1]["count"] > 0:
            idx = 1
        while idx < len(reversed_days) and reversed_days[idx]["count"] > 0:
            current_streak += 1
            idx += 1
            
    # Parse total contributions text from header if available
    header_total = total_contributions
    h2 = soup.find("h2", class_="f4 text-normal mb-2")
    if h2:
        m = re.search(r"([\d,]+)\s+contributions", h2.get_text())
        if m:
            header_total = int(m.group(1).replace(",", ""))

    payload = {
        "username": username,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "total_contributions": header_total if header_total >= total_contributions else total_contributions,
        "active_days": active_days,
        "longest_streak": longest_streak,
        "current_streak": current_streak,
        "days": days_data
    }
    
    return payload

def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub contributions data")
    parser.add_argument("--username", default="pallaviXD", help="GitHub username")
    parser.add_argument("--output", default="data/contributions.json", help="Output JSON path")
    args = parser.parse_args()
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    print(f"Fetching contributions for {args.username}...")
    data = fetch_contributions(args.username)
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    print(f"Successfully saved {len(data['days'])} days to {args.output}")
    print(f"Total contributions: {data['total_contributions']} | Active days: {data['active_days']} | Longest streak: {data['longest_streak']}d | Current streak: {data['current_streak']}d")

if __name__ == "__main__":
    main()
