import re
import urllib.parse
import requests
from bs4 import BeautifulSoup

# الرابط الأساسي الجديد لموقع أكوام
BASE_URL = "https://akwam.ss"

# هيدرز لمحاكاة متصفح حقيقي وتفادي الحجب
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": BASE_URL
}

def search_akwam(query):
    """البحث عن العنوان داخل موقع أكوام"""
    search_url = f"{BASE_URL}/search?q={urllib.parse.quote(query)}"
    try:
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        # البحث عن أول نتيجة في نتائج البحث
        entry = soup.select_one("div.entry-box, div.widget-body a.box")
        if entry:
            link = entry.get("href") if entry.name == "a" else entry.find("a")["href"]
            return link if link.startswith("http") else f"{BASE_URL}{link}"
    except Exception:
        pass
    return None

def extract_download_links(page_url):
    """استخراج روابط التحميل والمشاهدة المباشرة من صفحة العرض"""
    streams = []
    try:
        response = requests.get(page_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return streams
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # البحث عن أزرار التحميل/المشاهدة داخل الصفحة
        download_buttons = soup.select("a.link-download, a.btn-download, a[href*='/download/']")
        
        for btn in download_buttons:
            link = btn.get("href")
            quality_label = btn.get_text(strip=True) or "Akwam Server"
            
            if link:
                full_link = link if link.startswith("http") else f"{BASE_URL}{link}"
                streams.append({
                    "name": "MegaSource | Akwam",
                    "title": f"🎬 أكوام - {quality_label}",
                    "url": full_link
                })
    except Exception:
        pass
    return streams

def scrape(title, year=None, media_type="movie", season=None, episode=None):
    """الدالة الرئيسية التي تستدعيها إضافة MegaSource"""
    search_query = title
    if year and media_type == "movie":
        search_query += f" {year}"
    elif media_type == "series" and season and episode:
        search_query += f" الموسم {season} الحلقة {episode}"

    page_url = search_akwam(search_query)
    if not page_url and year:
        # المحاولة مرة أخرى بدون السنة في حال عدم ظهور نتائج
        page_url = search_akwam(title)

    if page_url:
        return extract_download_links(page_url)
    
    return []
