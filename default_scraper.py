import re
import urllib.parse
import urllib.request

TITLE = "Akwam Scraper"
VERSION = "1.1.0"
DESCRIPTION = "Scrapes direct playable video streams from Akwam for MegaSource"

BASE_URL = "https://akwam.ss"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": BASE_URL
}

def make_request(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as response:
            return response.read().decode('utf-8')
    except Exception:
        return None

def extract_direct_video_link(download_page_url):
    """فتح صفحة التحميل الوسيطة لاستخراج رابط الفيديو المباشر قابلا للتشغيل"""
    html = make_request(download_page_url)
    if not html:
        return None
    # البحث عن روابط الفيديو المباشرة mp4 أو سيرفر التشغيل
    video_match = re.search(r'href="([^"]+\.(?:mp4|mkv)[^"]*)"', html, re.IGNORECASE)
    if video_match:
        return video_match.group(1)
    
    # البحث عن رابط زر "تحميل/مشاهدة" المباشر داخل الصفحة الوسيطة
    direct_btn = re.search(r'class="[^\"]*download-link[^\"]*"[^\>]*href="([^"]+)"', html)
    if direct_btn:
        return direct_btn.group(1)
        
    return None

def get_streams(media_type: str, media_id: str, config: dict = None) -> list:
    streams = []
    
    # تحديد كلمة البحث
    query = config.get("query") if (config and "query" in config) else media_id
    
    # 1. البحث عن العنوان في أكوام
    search_url = f"{BASE_URL}/search?q={urllib.parse.quote(query)}"
    html = make_request(search_url)
    if not html:
        return streams

    # 2. استخراج رابط صفحة الفيلم/المسلسل
    match = re.search(r'href="(https://akwam\.ss/(?:movie|series|episode)/[^"]+)"', html)
    if not match:
        match = re.search(r'href="((?:/movie/|/series/|/episode/)[^"]+)"', html)
        page_url = f"{BASE_URL}{match.group(1)}" if match else None
    else:
        page_url = match.group(1)

    if not page_url:
        return streams

    # 3. جلب صفحة العرض واستخراج روابط الصفحات الوسيطة
    page_html = make_request(page_url)
    if not page_html:
        return streams

    download_pages = re.findall(r'href="([^"]+/download/[^"]+)"', page_html)
    
    # 4. جلب الرابط المباشر من أول رابطين لتفادي التبطئ (Timeout)
    for dl_page in download_pages[:2]:
        full_dl_page = dl_page if dl_page.startswith("http") else f"{BASE_URL}{dl_page}"
        direct_stream = extract_direct_video_link(full_dl_page)
        
        if direct_stream:
            streams.append({
                "name": "MegaSource | Akwam",
                "title": "🎬 أكوام - سيرفر تشغيل مباشر",
                "url": direct_stream
            })

    return streams
