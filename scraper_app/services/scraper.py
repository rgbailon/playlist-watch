"""
YouTube Playlist Scraper - Separate JSON files for playlists and videos
"""

import os
import json
import re
import time
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYLISTS_FILE = os.path.join(BASE_DIR, "playlists.json")
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")


def get_driver():
    """Create Selenium WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    # Additional stealth measures
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        """
        },
    )

    return driver


def scrape_playlists(query, max_playlists=15):
    """Scrape playlist search results"""
    driver = None
    playlists = []

    try:
        driver = get_driver()
        search_url = f"https://www.youtube.com/results?search_query={query}+playlist"

        print(f"🔍 Searching for '{query}' playlists...")
        driver.get(search_url)

        # Wait longer for page to load
        time.sleep(3)

        # Scroll to load results
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Try different selectors
        playlist_renderers = soup.find_all("ytd-playlist-renderer")

        if not playlist_renderers:
            # Try alternative: find links to playlists
            playlist_links = soup.find_all("a", href=re.compile(r"/playlist\?list="))
            for link in playlist_links[:max_playlists]:
                href = link.get("href", "")
                match = re.search(r"/playlist\?list=([A-Za-z0-9_-]+)", href)
                if match:
                    playlist_id = match.group(1)
                    title = link.get("title", "") or "Untitled Playlist"
                    thumbnail = (
                        f"https://img.youtube.com/vi/{playlist_id}/hqdefault.jpg"
                    )

                    if playlist_id not in [p.get("playlist_id") for p in playlists]:
                        playlists.append(
                            {
                                "playlist_id": playlist_id,
                                "url": f"https://www.youtube.com/playlist?list={playlist_id}",
                                "title": title[:200],
                                "thumbnail": thumbnail,
                                "video_count": 0,
                            }
                        )
        else:
            # Original method
            seen_ids = set()
            for renderer in playlist_renderers:
                if len(playlists) >= max_playlists:
                    break

                link = renderer.find("a", href=re.compile(r"/playlist\?list="))
                if not link:
                    continue

                href = link.get("href", "")
                match = re.search(r"/playlist\?list=([A-Za-z0-9_-]+)", href)
                if not match:
                    continue

                playlist_id = match.group(1)
                if playlist_id in seen_ids:
                    continue
                seen_ids.add(playlist_id)

                title = "Untitled Playlist"
                title_elem = renderer.find("yt-formatted-string")
                if title_elem:
                    title = title_elem.get_text(strip=True)
                if not title:
                    title = link.get("title", "") or "Untitled Playlist"

                thumbnail = f"https://img.youtube.com/vi/{playlist_id}/hqdefault.jpg"
                img = renderer.find("img")
                if img and img.get("src"):
                    thumbnail = img.get("src")

                playlists.append(
                    {
                        "playlist_id": playlist_id,
                        "url": f"https://www.youtube.com/playlist?list={playlist_id}",
                        "title": title[:200],
                        "thumbnail": thumbnail,
                        "video_count": 0,
                    }
                )

        print(f"  Found {len(playlists)} playlists")
        return playlists

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return playlists
    finally:
        if driver:
            driver.quit()


def scrape_playlist_videos(playlist_id, playlist_url, max_videos=50):
    """Scrape all videos from a playlist"""
    driver = None
    videos = []

    try:
        driver = get_driver()
        print(f"  📂 Scraping videos...")

        driver.get(playlist_url)
        time.sleep(1)

        last_height = driver.execute_script(
            "return document.documentElement.scrollHeight"
        )
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            new_height = driver.execute_script(
                "return document.documentElement.scrollHeight"
            )
            if new_height == last_height:
                break
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, "html.parser")
        video_elements = soup.find_all("ytd-playlist-video-renderer")

        for idx, elem in enumerate(video_elements[:max_videos], 1):
            link = elem.find("a", id="video-title")
            if not link:
                continue

            video_url = link.get("href", "")
            video_title = link.get("title", "") or link.get_text(strip=True)

            vid_match = re.search(r"v=([A-Za-z0-9_-]+)", video_url)
            if not vid_match:
                continue

            video_id = vid_match.group(1)
            thumb = elem.find("img")
            thumbnail = (
                thumb.get("src", "")
                if thumb
                else f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            )

            videos.append(
                {
                    "position": idx,
                    "video_id": video_id,
                    "title": video_title[:300],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": thumbnail,
                }
            )

        return videos

    except Exception as e:
        print(f"Error: {e}")
        return videos
    finally:
        if driver:
            driver.quit()


# JSON Functions
def get_playlists():
    """Load playlists from JSON"""
    if os.path.exists(PLAYLISTS_FILE):
        with open(PLAYLISTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_playlists(playlists):
    """Save playlists to JSON"""
    with open(PLAYLISTS_FILE, "w", encoding="utf-8") as f:
        json.dump(playlists, f, indent=2, ensure_ascii=False)


def get_playlist_videos(playlist_id):
    """Load videos for a specific playlist"""
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    video_file = os.path.join(VIDEOS_DIR, f"{playlist_id}.json")

    if os.path.exists(video_file):
        with open(video_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_playlist_videos(playlist_id, videos):
    """Save playlist videos to JSON"""
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    video_file = os.path.join(VIDEOS_DIR, f"{playlist_id}.json")
    with open(video_file, "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)


def get_playlist_by_id(playlist_id):
    """Get playlist by ID with videos"""
    playlists = get_playlists()
    for p in playlists:
        if p.get("playlist_id") == playlist_id:
            videos = get_playlist_videos(playlist_id)
            if videos:
                p["videos"] = videos
            return p
    return None


def get_video_by_id(video_id):
    """Find video by ID"""
    playlists = get_playlists()
    for playlist in playlists:
        videos = get_playlist_videos(playlist.get("playlist_id"))
        if videos:
            for video in videos:
                if video.get("video_id") == video_id:
                    return video, playlist
    return None, None


def search_and_scrape_playlists(query, max_playlists=12):
    """Main function: scrape playlists then scrape videos for each"""
    print(f"\n=== Scraping: {query} ===")

    # Step 1: Get playlists
    playlists = scrape_playlists(query, max_playlists)

    if not playlists:
        print("No playlists found")
        return None

    # Step 2: Get videos for each playlist
    for i, playlist in enumerate(playlists):
        print(f"\n[{i + 1}/{len(playlists)}] {playlist['title'][:30]}...")
        videos = scrape_playlist_videos(playlist["playlist_id"], playlist["url"])
        playlist["video_count"] = len(videos)

        if videos:
            save_playlist_videos(playlist["playlist_id"], videos)

        time.sleep(0.5)

    # Step 3: Save playlists
    save_playlists(playlists)

    print(f"\n✅ Done! {len(playlists)} playlists saved")
    return {
        "search_query": query,
        "scraped_at": datetime.now().isoformat(),
        "total_playlists": len(playlists),
    }


def load_from_json():
    """For compatibility - returns playlists with videos"""
    playlists = get_playlists()
    for p in playlists:
        videos = get_playlist_videos(p.get("playlist_id"))
        if videos:
            p["videos"] = videos
    return {"playlists": playlists} if playlists else None
