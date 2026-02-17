# YouTube Playlist Search - Django Web Application

A complete Django web application that searches YouTube for playlists using **BeautifulSoup + Selenium**, scrapes all video data, saves to JSON, and displays with a video player.

## ✨ Features

- 🔍 **Search YouTube** - Search for any keyword
- 📊 **Complete Scraping** - Extracts playlist titles, thumbnails, video counts
- 🎬 **Video Details** - Gets all video URLs, titles, and thumbnails
- 💾 **JSON Storage** - All data saved to `youtube_data.json`
- ▶️ **Video Player** - Multiple player options (Piped, Invidious, YouTube)
- 🎨 **Beautiful UI** - Dark theme with Bootstrap 5
- ⚡ **Fast Search** - Optimized scraping with BeautifulSoup

## 🚀 Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Start server:**
```bash
python manage.py runserver
```

4. **Open browser:** http://localhost:8000

## 📖 How It Works

### Search Flow:

1. User enters search term (e.g., "deftones")
2. Backend uses **Selenium + BeautifulSoup** to:
   - Search YouTube
   - Find all playlists
   - Visit each playlist
   - Extract all video data (title, URL, thumbnail)
3. Data saved to `youtube_data.json`
4. Results displayed as cards
5. Click playlist → See all videos
6. Click video → Play in embedded player

### Data Structure (youtube_data.json):

```json
{
  "search_query": "deftones",
  "scraped_at": "2026-02-17T...",
  "total_playlists": 10,
  "playlists": [
    {
      "playlist_id": "PLxxx",
      "url": "https://youtube.com/playlist?list=PLxxx",
      "title": "Deftones - Greatest Hits",
      "video_count": 25,
      "thumbnail": "https://...",
      "videos": [
        {
          "position": 1,
          "video_id": "xxx",
          "title": "Song Title",
          "url": "https://youtube.com/watch?v=xxx",
          "thumbnail": "https://..."
        }
      ]
    }
  ]
}
```

## 🎯 Usage

### Search for Playlists:
1. Go to http://localhost:8000
2. Enter search term (e.g., "deftones", "metallica")
3. Click Search
4. Wait 30-60 seconds for complete scrape
5. View results with thumbnails and video counts

### View Playlist:
1. Click any playlist card
2. See all videos with thumbnails
3. Click any video to play

### Video Player Options:
- **Piped** (default) - Privacy-focused, no ads
- **Invidious** - Alternative frontend
- **YouTube** - Official embed

## 📁 Project Structure

```
web scraping/
├── manage.py
├── db.sqlite3
├── youtube_data.json          # Scraped data storage
├── requirements.txt
├── README.md
├── deftones_search/           # Django project
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── scraper_app/               # Main application
│   ├── models.py              # Database models (fallback)
│   ├── views.py               # View functions
│   ├── urls.py
│   ├── services/
│   │   └── scraper.py         # BeautifulSoup scraper
│   └── templates/
│       └── scraper_app/
│           ├── base.html
│           ├── home.html
│           ├── playlist_detail.html
│           └── video_player.html
└── static/
    └── css/
        └── style.css
```

## 🛠 Technologies

| Component | Technology |
|-----------|------------|
| Backend | Django 5.x |
| Scraping | Selenium, BeautifulSoup4 |
| Frontend | Bootstrap 5, Bootstrap Icons |
| Data Storage | JSON file + SQLite (optional) |
| Video Players | Piped, Invidious, YouTube |

## ⚙️ Configuration

### Scraper Settings (scraper_app/services/scraper.py):

```python
# Adjust these values to control scraping:
max_playlists = 10          # Max playlists to scrape
max_videos_per_playlist = 50  # Max videos per playlist
```

### JSON File Location:
Default: `youtube_data.json` in project root

## 🔧 Admin Panel

Access at: http://localhost:8000/admin/

Create superuser:
```bash
python manage.py createsuperuser
```

## 📝 Notes

- **First search takes 30-60 seconds** - Complete scraping of all playlists and videos
- **Subsequent searches are instant** - Data cached in JSON file
- **Headless browser** - No visible Chrome window
- **Respect YouTube ToS** - For educational use only

## 🎨 Screenshots

### Home Page:
- Search box at top
- Playlist cards with thumbnails
- Video count badges

### Playlist Detail:
- All videos displayed as cards
- Video thumbnails and titles
- Position numbers

### Video Player:
- Embedded player (Piped/Invidious/YouTube)
- Video info card
- Up next sidebar

## 📄 License

For educational purposes only. Respect YouTube's Terms of Service.

## 🙏 Credits

- Built with Django & BeautifulSoup
- Video players: Piped, Invidious
- UI: Bootstrap 5
