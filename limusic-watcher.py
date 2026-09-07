#!/usr/bin/env python3
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

# Configuration Paths
BASE_DIR = Path.home() / "projects" / "steelseries-audio"
SCRIPT_PATH = str(BASE_DIR / "steelseries-audio")
DB_PATH = str(BASE_DIR / "audio_cache.db")

# Profile Mapping Blueprints (Expanded with fallback terms for modern artists)
PROFILE_RULES = {
    "math-metal": r"math rock|progressive metal|djent|mathcore|progressive rock|post-hardcore|midwest emo",
    "sludge-prog": r"sludge metal|doom metal|post-metal|stoner rock|sludge|grunge",
    "phonk-rap": r"phonk|hip hop|rap|trap|boom bap|underground rap|alternative rap|cloud rap",
    "electro-synth": r"electro|electronic|house|synthwave|techno|industrial|indie pop|indie rock|alternative rock",
    "kung-faux": r"funk|disco|old school hip hop|freestyle|r&b|soul"
}

# ANSI Styling Configurations
C_CYAN, C_GREEN, C_YELLOW, C_MAGENTA, C_BOLD, C_RESET = "\033[36m", "\033[32m", "\033[33m", "\033[35m", "\033[1m", "\033[0m"

def init_database():
    """Ensures the local SQLite database exists and is properly structured."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artist_genres (
            artist TEXT PRIMARY KEY,
            genre_summary TEXT,
            profile TEXT
        );
    """)
    conn.commit()
    conn.close()

def query_musicbrainz(artist: str) -> tuple:
    """Two-Stage lookup: Finds the artist MBID, then explicitly extracts genre strings."""
    # Stage 1: Search for the Artist Entity to harvest the MBID
    encoded_query = urllib.parse.quote(f'artist:"{artist}"')
    search_url = f"https://musicbrainz.org/ws/2/artist?query={encoded_query}&fmt=json"

    headers = {"User-Agent": "LimusicArena7Optimizer/1.0.0 ( mailto:matty@localhost )"}
    time.sleep(1.1) # Strict baseline API limit safeguard

    try:
        # Fetch the Search Payload
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as response:
            search_data = json.loads(response.read().decode('utf-8'))
            artists = search_data.get("artists", [])
            if not artists:
                return "None (Using Audiophile Reference)", "audiophile"

            # Isolate the highest scoring match element and pull its unique MBID
            best_match = artists[0]
            mbid = best_match.get("id")
            if not mbid:
                return "None (Using Audiophile Reference)", "audiophile"

        # Stage 2: Direct Lookup using the MBID to pull explicit genre sub-resources
        time.sleep(1.1) # Maintain rate limiting spacing
        lookup_url = f"https://musicbrainz.org/ws/2/artist/{mbid}?inc=genres+tags&fmt=json"

        req = urllib.request.Request(lookup_url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as response:
            artist_data = json.loads(response.read().decode('utf-8'))

            # Combine both explicit genre classifications and folksonomy tags safely
            genre_list = artist_data.get("genres", []) or []
            tag_list = artist_data.get("tags", []) or []

            raw_elements = [g.get("name", "").lower() for g in genre_list if g.get("name")]
            raw_elements += [t.get("name", "").lower() for t in tag_list if t.get("name")]

            genres_str = " ".join(raw_elements)

            if not genres_str:
                return "Genre Tags Unindexed on Registry", "audiophile"

            # Evaluate against regular expression slates
            for profile, pattern in PROFILE_RULES.items():
                if re.search(pattern, genres_str):
                    display_name = profile.replace("-", " ").title()
                    return display_name, profile

            return f"Unmapped Genres ({', '.join(raw_elements[:2])})", "audiophile"

    except Exception as e:
        print(f"  {C_YELLOW}↳ [NETWORK WARN] Pipeline Query Interrupted:{C_RESET} {e}")

    return "None (Using Audiophile Reference)", "audiophile"

def process_track_change(artist: str):
    """Processes track updates using local caching and direct runtime injections."""
    print(f"{C_CYAN}[MPRIS Active]{C_RESET} Track Artist: {C_BOLD}{artist}{C_RESET}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT genre_summary, profile FROM artist_genres WHERE LOWER(artist) = LOWER(?);", (artist,))
    row = cursor.fetchone()

    if row:
        matched_genre, profile = row[0], row[1]
        print(f"  {C_GREEN}↳ [CACHE HIT]{C_RESET} Restored local map from SQLite database node.")
    else:
        print(f"  {C_YELLOW}↳ [CACHE MISS]{C_RESET} Querying MusicBrainz live registry...")
        matched_genre, profile = query_musicbrainz(artist)

        cursor.execute("INSERT OR IGNORE INTO artist_genres (artist, genre_summary, profile) VALUES (?, ?, ?);",
                       (artist, matched_genre, profile))
        conn.commit()
        print(f"  {C_GREEN}↳ [CACHE WRITE]{C_RESET} Committed data mappings to local database.")

    conn.close()

    print(f"  {C_MAGENTA}↳ Genre Array Classification:{C_RESET} {matched_genre}")
    print(f"  {C_GREEN}↳ Applying Real-Time EQ Target:{C_RESET} {profile}\n")

    subprocess.run([SCRIPT_PATH, "profile", profile], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    init_database()
    print(f"{C_CYAN}{C_BOLD}Launching Robust Python Genre-Sync Engine (SQLite3)...{C_RESET}")
    print("Listening securely for native MPRIS track updates via playerctl...")

    cmd = ["playerctl", "--player=limusic", "metadata", "--format", "{{ artist }}", "--follow"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1)

    last_seen_artist = ""

    try:
        for line in iter(proc.stdout.readline, ""):
            artist = line.strip()
            if not artist or artist == last_seen_artist:
                continue

            last_seen_artist = artist
            process_track_change(artist)
    except KeyboardInterrupt:
        print("\nShutting down audio tracking daemon cleanly.")
        proc.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
