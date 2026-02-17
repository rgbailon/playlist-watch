"""
YouTube Playlist Scraper - Complete BeautifulSoup Implementation
Searches playlists, extracts all data, saves to JSON, and displays in web app
"""

import time
import re
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# JSON file path
DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "youtube_data.json"
)


def get_driver():
    """Create and return an optimized Selenium WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    return driver


def build_search_url(query, max_results=10, sort_by="relevance"):
    """
    Build optimized YouTube search URL with filters
    sort_by: relevance, upload_date, view_count"""
    base_url = "https://www.youtube.com/results"

    search_query = f"{query} playlist"

    params = {"search_query": search_query, "sp": get_sort_param(sort_by)}

    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{base_url}?{query_string}"


def get_sort_param(sort_by):
    """Get YouTube search parameter for sorting"""
    sort_params = {
        "relevance": "CAI%253D",
        "upload_date": "CAI%253D",
        "view_count": "CAyA%253D",
        "rating": "CAyA%253D",
    }
    return sort_params.get(sort_by, "CAI%253D")


def search_and_scrape_playlists(
    query, max_playlists=15, max_videos_per_playlist=50, sort_by="view_count"
):
    """
    Complete scraping workflow:
    1. Search YouTube for playlists with optimized query
    2. Visit each playlist
    3. Extract all video data
    4. Save to JSON file
    """
    driver = None
    all_data = {
        "search_query": query,
        "scraped_at": datetime.now().isoformat(),
        "total_playlists": 0,
        "playlists": [],
    }

    try:
        search_url = build_search_url(query, max_playlists, sort_by)
        driver = get_driver()

        print(f"🔍 Searching for '{query}' playlists...")
        driver.get(search_url)
        time.sleep(0.5)

        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.3)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        playlist_links = soup.find_all("a", href=re.compile(r"/playlist\?list="))
        unique_playlists = []
        seen_ids = set()
        for link in playlist_links:
            match = re.search(r"/playlist\?list=([A-Za-z0-9_-]+)", link.get("href", ""))
            if match and match.group(1) not in seen_ids:
                seen_ids.add(match.group(1))
                unique_playlists.append(link)

        print(f"  Found {len(unique_playlists)} unique playlist links")

        playlists_scraped = 0

        for link in playlist_links:
            if playlists_scraped >= max_playlists:
                break

            href = link.get("href", "")
            pl_match = re.search(r"/playlist\?list=([A-Za-z0-9_-]+)", href)

            if not pl_match:
                continue

            pl_id = pl_match.group(1)
            pl_url = f"https://www.youtube.com/playlist?list={pl_id}"

            print(f"\n📁 Scraping playlist: {pl_id}")

            # Step 2: Visit playlist and extract data
            playlist_data = scrape_playlist_details(
                driver, pl_id, pl_url, max_videos_per_playlist
            )

            if playlist_data:
                all_data["playlists"].append(playlist_data)
                playlists_scraped += 1
                print(f"  ✅ Scraped {len(playlist_data.get('videos', []))} videos")

        all_data["total_playlists"] = playlists_scraped

        # Step 3: Save to JSON
        save_to_json(all_data)

        print(f"\n✅ Complete! Scraped {playlists_scraped} playlists")
        print(f"📄 Data saved to: {DATA_FILE}")

        return all_data

    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if driver:
            driver.quit()


def scrape_playlist_details(driver, playlist_id, playlist_url, max_videos=50):
    """
    Visit a playlist and extract all details including videos
    """
    try:
        driver.get(playlist_url)
        time.sleep(1)

        # Scroll to load all videos
        last_height = driver.execute_script(
            "return document.documentElement.scrollHeight"
        )
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            new_height = driver.execute_script(
                "return document.documentElement.scrollHeight"
            )
            if new_height == last_height:
                break
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract playlist info
        playlist_data = {
            "playlist_id": playlist_id,
            "url": playlist_url,
            "title": "",
            "video_count": 0,
            "thumbnail": "",
            "videos": [],
        }

        # Get playlist title
        title_elem = soup.find("yt-formatted-string", id="text-container")
        if not title_elem:
            title_elem = soup.find("h1", {"class": re.compile(r"style-scope")})
        if title_elem:
            playlist_data["title"] = title_elem.get_text(strip=True)[:200]

        # Get video count
        count_elem = soup.find("yt-formatted-string", string=re.compile(r"\d+\s*video"))
        if count_elem:
            playlist_data["video_count"] = count_elem.get_text(strip=True)

        # Get thumbnail - try multiple methods
        thumb_img = soup.find("img", class_=re.compile(r"yt-img-shadow"))
        if thumb_img:
            playlist_data["thumbnail"] = thumb_img.get("src", "")

        # If no thumbnail, try to get first video's thumbnail
        if not playlist_data["thumbnail"]:
            video_elements = soup.find_all("ytd-playlist-video-renderer")
            if video_elements:
                first_video = video_elements[0]
                link = first_video.find("a", id="video-title")
                if link:
                    video_url = link.get("href", "")
                    vid_match = re.search(r"v=([A-Za-z0-9_-]+)", video_url)
                    if vid_match:
                        video_id = vid_match.group(1)
                        playlist_data["thumbnail"] = (
                            f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                        )

        # Final fallback
        if not playlist_data["thumbnail"]:
            playlist_data["thumbnail"] = (
                f"https://img.youtube.com/vi/{playlist_id}/hqdefault.jpg"
            )

        # Extract all videos
        video_elements = soup.find_all("ytd-playlist-video-renderer")

        for idx, elem in enumerate(video_elements[:max_videos], 1):
            link = elem.find("a", id="video-title")
            if not link:
                continue

            video_url = link.get("href", "")
            video_title = link.get("title", "") or link.get_text(strip=True)

            # Extract video ID
            vid_match = re.search(r"v=([A-Za-z0-9_-]+)", video_url)
            if not vid_match:
                continue

            video_id = vid_match.group(1)

            # Get video thumbnail
            thumb_elem = elem.find("img", class_=re.compile(r"yt-img-shadow"))
            video_thumbnail = (
                thumb_elem.get("src", "")
                if thumb_elem
                else f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            )

            playlist_data["videos"].append(
                {
                    "position": idx,
                    "video_id": video_id,
                    "title": video_title[:300],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": video_thumbnail,
                }
            )

        playlist_data["video_count"] = len(playlist_data["videos"])

        return playlist_data

    except Exception as e:
        print(f"  Error scraping playlist: {e}")
        return None


def save_to_json(data):
    """Save scraped data to JSON file"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  💾 Saved to {DATA_FILE}")


def load_from_json():
    """Load data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def get_playlist_by_id(playlist_id):
    """Get a specific playlist from JSON data"""
    data = load_from_json()
    if not data:
        return None

    for playlist in data.get("playlists", []):
        if playlist.get("playlist_id") == playlist_id:
            return playlist
    return None


def get_video_by_id(video_id):
    """Get a specific video from JSON data"""
    data = load_from_json()
    if not data:
        return None, None

    for playlist in data.get("playlists", []):
        for video in playlist.get("videos", []):
            if video.get("video_id") == video_id:
                return video, playlist
    return None, None
