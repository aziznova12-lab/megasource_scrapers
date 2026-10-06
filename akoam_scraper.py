import requests
from bs4 import BeautifulSoup
from megasource import scraper

AKOAM_BASE = "https://ak.sv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@scraper(
    name="Akoam",
    id="akoam_scraper",
    version="1.0.0",
    description="جلب الأفلام والمسلسلات العربية والأجنبية من موقع أكوام"
)
class AkoamScraper:

    @scraper.search
    def search(self, query: str, type_: str = "movie"):
        results = []
        search_url = f"{AKOAM_BASE}/search?q={requests.utils.quote(query)}"
        
        try:
            res = requests.get(search_url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                for box in soup.select(".entry-box, .box"):
                    title_elem = box.select_one(".title, h3, a.box-link")
                    img_elem = box.select_one("img")
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get("href") if title_elem.name == "a" else title_elem.find("a")["href"]
                        poster = img_elem.get("src") or img_elem.get("data-src") if img_elem else ""
                        
                        if link and not link.startswith("http"):
                            link = AKOAM_BASE + link
                        
                        results.append({
                            "title": title,
                            "url": link,
                            "poster": poster,
                            "type": type_
                        })
        except Exception as e:
            print(f"[Akoam Search Error]: {e}")
            
        return results

    @scraper.get_streams
    def get_streams(self, item_url: str):
        streams = []
        try:
            res = requests.get(item_url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                
                # البحث عن زر المشاهدة أو التحميل المباشر
                download_btn = soup.select_one("a.link-download, a[href*='download'], a.download-link")
                if download_btn and download_btn.get("href"):
                    streams.append({
                        "name": "Akoam Server",
                        "title": "مشاهدة مباشرة - Akoam",
                        "url": download_btn.get("href"),
                        "quality": "1080p"
                    })
                
                # البحث عن سيرفرات التشغيل داخل iframe
                iframe = soup.select_one("iframe[src]")
                if iframe and iframe.get("src"):
                    streams.append({
                        "name": "Akoam Stream",
                        "title": "مشغّل أكوام الفرعي",
                        "url": iframe.get("src"),
                        "quality": "720p"
                    })
        except Exception as e:
            print(f"[Akoam Stream Error]: {e}")
            
        return streams
