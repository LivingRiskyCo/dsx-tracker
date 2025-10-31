#!/usr/bin/env python3
"""
Fetch CPL Fall 2025 U9 Division standings from GotSport group pages and
consolidate into a single division rankings CSV.

Inputs: Hardcoded list of GotSport Results URLs (group pages)
Output: CPL_Fall_2025_Division_Rankings.csv

Columns: Rank, Team, GP, W, L, D, GF, GA, GD, Pts, PPG, StrengthIndex,
         SourceURL, Division, League
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

GROUP_URLS = [
    # Provided by user
    "https://system.gotsport.com/org_event/events/43740/results?group=380753",
    "https://system.gotsport.com/org_event/events/43740/results?group=380748",
    "https://system.gotsport.com/org_event/events/43740/results?group=380749",
    "https://system.gotsport.com/org_event/events/43740/results?group=380746",
    "https://system.gotsport.com/org_event/events/43740/results?group=380750",
    "https://system.gotsport.com/org_event/events/43740/results?group=380751",
    "https://system.gotsport.com/org_event/events/43740/results?group=380752",
    "https://system.gotsport.com/org_event/events/43740/results?group=380747",
    "https://system.gotsport.com/org_event/events/43740/results?group=380754",
    "https://system.gotsport.com/org_event/events/43740/results?group=406317",
]

OUTPUT_FILE = "CPL_Fall_2025_Division_Rankings.csv"


def compute_strength_index(ppg: float, gd_per_game: float) -> float:
    ppg_norm = max(0.0, min(3.0, ppg)) / 3.0 * 100.0
    gdpg_norm = (max(-5.0, min(5.0, gd_per_game)) + 5.0) / 10.0 * 100.0
    return round(0.7 * ppg_norm + 0.3 * gdpg_norm, 1)


def parse_group(url: str) -> pd.DataFrame:
    # Set a real browser UA; some GotSport pages hide tables from bots
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    resp = requests.get(url, timeout=20, headers=headers)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # First try pandas read_html (works if tables are straightforward)
    try:
        tables = pd.read_html(resp.text)
    except ValueError:
        tables = []

    parsed = None
    if tables:
        # Heuristics: choose table with W/L/D and PTS/Points
        for t in tables:
            cols = [str(c).strip().lower() for c in t.columns]
            if ("w" in cols and ("pts" in cols or "points" in cols)) or (
                any(c in cols for c in ["mp", "gp", "matches"]) and "w" in cols
            ):
                parsed = t
                break

    if parsed is None:
        # Manual parse via BeautifulSoup (more robust)
        tables_html = soup.find_all("table")
        best = None
        for tbl in tables_html:
            # Extract header
            headers_row = tbl.find("thead")
            if headers_row:
                ths = [th.get_text(strip=True) for th in headers_row.find_all("th")]
            else:
                first_tr = tbl.find("tr")
                ths = [th.get_text(strip=True) for th in first_tr.find_all(["th", "td"]) ] if first_tr else []

            lower_ths = [h.lower() for h in ths]
            if not lower_ths:
                continue
            # Look for standing-like table
            if ("team" in lower_ths) and ("w" in lower_ths or "wins" in lower_ths) and ("pts" in lower_ths or "points" in lower_ths):
                # Parse body rows
                rows = []
                body = tbl.find("tbody") or tbl
                for tr in body.find_all("tr"):
                    tds = tr.find_all("td")
                    if not tds:
                        continue
                    cells = [td.get_text(strip=True) for td in tds]
                    rows.append(cells)
                # Build DataFrame with as many columns as headers
                if rows:
                    # Adjust row length to headers length
                    max_len = max(len(r) for r in rows)
                    # If header shorter, pad
                    if len(ths) < max_len:
                        # create generic headers
                        ths_extended = ths + [f"col{i}" for i in range(len(ths), max_len)]
                    else:
                        ths_extended = ths
                    parsed = pd.DataFrame(rows, columns=ths_extended[:max_len])
                    best = parsed
                    break
        if best is not None:
            parsed = best

    if parsed is None or parsed.empty:
        # No table found on this page
        return pd.DataFrame()

    df = parsed.copy()
    # Normalize columns
    colmap = {}
    for c in df.columns:
        cl = str(c).strip().lower()
        if cl in ("team", "team name"):
            colmap[c] = "Team"
        elif cl in ("mp", "gp", "games", "matches", "played"):
            colmap[c] = "GP"
        elif cl == "w":
            colmap[c] = "W"
        elif cl == "l":
            colmap[c] = "L"
        elif cl == "d":
            colmap[c] = "D"
        elif cl in ("gf", "goals for"):
            colmap[c] = "GF"
        elif cl in ("ga", "goals against"):
            colmap[c] = "GA"
        elif cl in ("gd", "goal difference"):
            colmap[c] = "GD"
        elif cl in ("pts", "points"):
            colmap[c] = "Pts"
    df = df.rename(columns=colmap)

    # Keep needed columns
    keep = ["Team", "GP", "W", "L", "D", "GF", "GA", "GD", "Pts"]
    for k in keep:
        if k not in df.columns:
            df[k] = 0

    # Coerce to numeric
    for k in ["GP", "W", "L", "D", "GF", "GA", "GD", "Pts"]:
        df[k] = pd.to_numeric(df[k], errors="coerce").fillna(0)

    # Compute PPG and StrengthIndex
    df["PPG"] = df.apply(lambda r: (r["Pts"] / r["GP"]) if r["GP"] > 0 else 0, axis=1)
    df["GF_PG"] = df.apply(lambda r: (r["GF"] / r["GP"]) if r["GP"] > 0 else 0, axis=1)
    df["GA_PG"] = df.apply(lambda r: (r["GA"] / r["GP"]) if r["GP"] > 0 else 0, axis=1)
    df["GD_PG"] = df["GF_PG"] - df["GA_PG"]
    df["StrengthIndex"] = df.apply(lambda r: compute_strength_index(r["PPG"], r["GD_PG"]), axis=1)

    # Add metadata
    # Division name may be in the page header; keep generic label
    df["SourceURL"] = url
    df["Division"] = "CPL U9"
    df["League"] = "CPL Fall 2025"
    df["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Rank within this group (by PPG then GD then GF)
    df = df.sort_values(["PPG", "GD", "GF"], ascending=[False, False, False]).reset_index(drop=True)
    df["Rank"] = range(1, len(df) + 1)

    return df[
        [
            "Rank",
            "Team",
            "GP",
            "W",
            "L",
            "D",
            "GF",
            "GA",
            "GD",
            "Pts",
            "PPG",
            "StrengthIndex",
            "SourceURL",
            "Division",
            "League",
            "last_updated",
        ]
    ]


def main():
    frames = []
    for url in GROUP_URLS:
        try:
            df = parse_group(url)
            if not df.empty:
                frames.append(df)
        except Exception as e:
            print(f"[WARN] Failed to parse {url}: {e}")

    if not frames:
        print("[ERROR] No standings found for CPL Fall 2025")
        return False

    combined = pd.concat(frames, ignore_index=True)
    # Deduplicate on Team (keep the best record by GP)
    combined = combined.sort_values(["Team", "GP"], ascending=[True, False])
    combined = combined.drop_duplicates(subset=["Team"], keep="first").reset_index(drop=True)

    combined.to_csv(OUTPUT_FILE, index=False)
    print(f"[OK] Saved {len(combined)} teams to {OUTPUT_FILE}")
    return True


if __name__ == "__main__":
    main()


