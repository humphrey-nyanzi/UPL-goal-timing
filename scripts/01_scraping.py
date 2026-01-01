#!/usr/bin/env python
"""
Scrape UPL match and goal data from the official website.

Usage:
    python scripts/01_scraping.py --season 2025-26
"""

import sys
import argparse
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import pandas as pd

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import USER_AGENT, UPL_CALENDAR_URL, UPL_EVENT_URL_PREFIX, REQUEST_TIMEOUT, DATA_RAW
from src.dataset import save_dataframe


def fetch_match_urls(season: str, headers: dict) -> list:
    """
    Fetch all match URLs for a given season.

    Parameters
    ----------
    season : str
        Season string (e.g., "2025-26")
    headers : dict
        HTTP headers including User-Agent

    Returns
    -------
    list
        List of match URLs
    """
    calendar_url = UPL_CALENDAR_URL.format(season=season)
    print(f"Fetching match calendar from: {calendar_url}")

    try:
        response = requests.get(calendar_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        print(f"✓ Status: {response.status_code}")
    except Exception as e:
        print(f"✗ Failed to fetch calendar: {e}")
        raise

    soup = BeautifulSoup(response.content, 'html.parser')
    matches_table = soup.select_one('div[class="sp-template sp-template-event-blocks"]')

    if not matches_table:
        print("✗ Could not find matches table on page")
        return []

    match_urls = []
    for link in matches_table.find_all('a'):
        url = link.get('href')
        if url and url.startswith(UPL_EVENT_URL_PREFIX):
            match_urls.append(url)

    # Remove duplicates
    match_urls = list(set(match_urls))
    print(f"✓ Found {len(match_urls)} unique matches")
    return match_urls


def parse_match_details(match_html) -> dict:
    """Extract match details and goals from match HTML."""
    soup = BeautifulSoup(match_html, 'html.parser')

    # Get teams
    title_tag = soup.select_one('h1[class="entry-title"]')
    if title_tag:
        teams = title_tag.get_text(strip=True).split(' vs ')
        home_team = teams[0].strip() if len(teams) > 0 else None
        away_team = teams[1].strip() if len(teams) > 1 else None
    else:
        home_team = away_team = None

    # Get event details
    event_details_table = soup.select_one('table[class="sp-event-details sp-data-table sp-scrollable-table"]')
    match_details = {}

    if event_details_table:
        event_table_headers = [th.get_text(strip=True) for th in event_details_table.select('th')]
        data = [td.get_text(strip=True) for td in event_details_table.select('tbody td')]
        match_details = dict(zip(event_table_headers, data))

    match_details.update({'home_team': home_team, 'away_team': away_team})

    # Parse goals
    goals = []
    timeline = soup.select_one('div[class="sp-template sp-template-timeline sp-template-event-timeline sp-template-vertical-timeline"]')

    if timeline:
        for icon in timeline.find_all('i', class_='sp-icon-soccerball'):
            tr = icon.find_parent('tr')
            if not tr:
                continue

            tds = tr.find_all('td')
            minute = tds[1].get_text(strip=True) if len(tds) > 1 else ''

            # Determine goal type
            icon_title = (icon.get('title') or '').strip().lower()
            if icon_title == 'own goals' or 'own goal' in icon_title:
                goal_type = 'Own Goal'
            elif '(P)' in minute or minute.strip().upper().endswith('P'):
                goal_type = 'Penalty'
            elif 'OG' in minute.upper():
                goal_type = 'Own Goal'
            else:
                goal_type = 'Regular'

            minute = minute.replace("'", "").replace("(P)", "").replace("OG", "").strip()

            # Determine side (home or away)
            icon_td = icon.find_parent('td')
            side_cell_index = tds.index(icon_td) if (icon_td and icon_td in tds) else 2
            side = 'home' if side_cell_index == 0 else 'away'

            # Get player name
            player_text = tds[side_cell_index].get_text(" ", strip=True)
            player_text = re.sub(r'^\s*\d+\.*\s*', '', player_text).strip()

            goals.append({
                'goal_minute': minute,
                'team_side': side,
                'player_name': player_text,
                'goal_type': goal_type
            })

    return match_details, goals


def scrape_season(season: str) -> pd.DataFrame:
    """
    Scrape all goal data for a season.

    Parameters
    ----------
    season : str
        Season string (e.g., "2025-26")

    Returns
    -------
    pd.DataFrame
        Dataframe with all goals and match details
    """
    headers = {'User-Agent': USER_AGENT}
    match_urls = fetch_match_urls(season, headers)

    all_rows = []

    print(f"\nScraping {len(match_urls)} matches...")
    for i, url in enumerate(match_urls, 1):
        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            match_details, goals = parse_match_details(response.content)

            # Create rows
            if goals:
                for goal in goals:
                    row = {**match_details, **goal}
                    if isinstance(row, dict):
                        all_rows.append(row)
            else:
                # Add row even if no goals
                empty_goal_row = {
                    'goal_minute': None,
                    'team_side': None,
                    'player_name': None,
                    'goal_type': None
                }
                row = {**match_details, **empty_goal_row}
                all_rows.append(row)

            if i % 10 == 0:
                print(f"  ✓ Processed {i}/{len(match_urls)} matches")

        except Exception as e:
            print(f"  ✗ Error processing {url}: {e}")
            continue

    # Create dataframe
    if all_rows:
        df = pd.DataFrame(all_rows)
        goal_cols = ['goal_minute', 'team_side', 'player_name', 'goal_type']
        match_cols = [col for col in df.columns if col not in goal_cols]
        existing_goal_cols = [c for c in goal_cols if c in df.columns]
        df = df[match_cols + existing_goal_cols]
    else:
        df = pd.DataFrame(columns=['home_team', 'away_team', 'goal_minute', 'team_side', 'player_name', 'goal_type'])

    return df


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Scrape UPL match and goal data')
    parser.add_argument('--season', type=str, default='2025-26', help='Season to scrape (e.g., 2025-26)')
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"UPL Goal Data Scraper - Season {args.season}")
    print(f"{'='*60}\n")

    try:
        # Scrape data
        df = scrape_season(args.season)

        # Save to data/raw/
        season_key = args.season.replace("-", "_")
        output_path = DATA_RAW / f"upl_goals_{season_key}.csv"
        save_dataframe(df, output_path)

        print(f"\n✓ Scraping complete! Data saved to: {output_path}")
        return 0

    except Exception as e:
        print(f"\n✗ Scraping failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
