import re
import urllib.parse
import urllib.request
import json

# معلومات السكريبت القياسية لـ MegaSource
TITLE = "Akwam Scraper"
VERSION = "1.0.0"
DESCRIPTION = "Scrapes streams from Akwam for MegaSource"

BASE_URL = "https://akwam.ss"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": BASE_URL
}

def make_request(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8')
    except Exception:
        return None

def get_streams(media_type: str, media_id: str, config: dict = None) -> list:
    """
    الدالة الرئيسية التي يستدعيها MegaSource تلقائياً
    """
    streams = []
    
    # 1. تحويل IMDB ID أو العنوان الممرر من Stremio
    query = config.get("query") if config and "query" in config else media_id
    
    # 2. البحث في موقع أكوام
    search_url = f"{BASE_URL}/search?q={urllib.parse.quote(query)}"
    html = make_request(search_url)
    if not html:
        return streams

    # 3. استخراج أول رابط نتيجة من البحث
    match = re.search(r'href="(https://akwam\.ss/movie/[^"]+|https://akwam\.ss/series/[^"]+)"', html)
    if not match:
        match = re.search(r'href="(/movie/[^"]+|/series/[^"]+)"', html)
        page_url = f"{BASE_URL}{match.group(1)}" if match else None
    else:
        page_url = match.group(1)

    if not page_url:
        return streams

    # 4. جلب صفحة العرض واستخراج روابط التحميل/المشاهدة
    page_html = make_request(page_url)
    if not page_html:
        return streams

    download_links = re.findall(r'href="([^"]+/download/[^"]+)"', page_html)
    for link in download_links:
        full_link = link if link.startswith("http") else f"{BASE_URL}{link}"
        streams.append({
            "name": "MegaSource | Akwam",
            "title": "🎬 سيرفر أكوام مباشر",
            "url": full_link
        })

    return streams
