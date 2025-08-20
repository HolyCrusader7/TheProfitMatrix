import os, random, csv, re, feedparser
from utils import ensure_dir, clean_html

STOPWORDS=set()
def load_stopwords(path):
    global STOPWORDS
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            STOPWORDS=set(w.strip().lower() for w in f if w.strip())

def pick_mode(today, force_mode=None):
    if force_mode in ("evergreen","news"): return force_mode
    return "evergreen" if (today.toordinal()%2==0) else "news"

def load_evergreen_csv(path):
    rows=[]
    with open(path,"r",encoding="utf-8") as f:
        r=csv.DictReader(f)
        for row in r: rows.append(row)
    random.shuffle(rows); return rows

def fetch_news_candidates(max_items=15):
    feeds=[
        "https://feeds.reuters.com/reuters/businessNews",
        "https://news.google.com/rss/search?q=finance%20OR%20business&hl=en-GB&gl=GB&ceid=GB:en",
        "https://www.cnbc.com/id/10001147/device/rss/rss.html"
    ]
    items=[]; import requests, html
    for url in feeds:
        try:
            fp=feedparser.parse(url)
            for e in fp.entries[:10]:
                title = getattr(e, "title", "") or ""
                summary = getattr(e, "summary", "") or getattr(e, "description", "") or ""
                link = getattr(e, "link", "") or ""
                src = fp.feed.get("title","News")
                if title and link:
                    items.append({"title":title,"summary":summary,"link":link,"source":src})
        except Exception:
            continue
        if len(items)>=max_items: break
    random.shuffle(items)
    return items[:max_items]

def extract_query_from_title(title):
    words=re.findall(r"[A-Za-z]{3,}", title.lower())
    words=[w for w in words if w not in STOPWORDS]
    if not words: return "stock market"
    return " ".join(words[:2])
