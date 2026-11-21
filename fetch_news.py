"""신뢰할 수 있는 매체/공식기관 RSS를 모아 news.json 생성 (표준 라이브러리만 사용)"""
import json, re, html, math, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta

# (이름, URL, 신뢰등급, 증시 키워드 필터 여부)
FEEDS = [
 ("Federal Reserve","https://www.federalreserve.gov/feeds/press_all.xml","공식기관",False),
 ("BLS","https://www.bls.gov/feed/bls_latest.rss","공식기관",False),
 ("CNBC Markets","https://www.cnbc.com/id/10000664/device/rss/rss.html","주요언론",False),
 ("CNBC Economy","https://www.cnbc.com/id/20910258/device/rss/rss.html","주요언론",False),
 ("MarketWatch","https://feeds.content.dowjones.io/public/rss/mw_topstories","주요언론",False),
 ("WSJ Markets","https://feeds.content.dowjones.io/public/rss/RSSMarketsMain","주요언론",False),
 ("NYT Business","https://rss.nytimes.com/services/xml/rss/nyt/Business.xml","주요언론",True),
]
KEY = re.compile(r"stock|market|fed\b|inflation|rate|economy|jobs|earnings|treasury|dow|nasdaq|s&p|oil|dollar|tariff|gdp|bank|wall street", re.I)
STOP = set("this that with from have will would about after over into more than they their were been says said what when your also could which while amid just".split())
now = datetime.now(timezone.utc)

def clean(t): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t or ""))).strip()
def parse_date(s):
    try: d = parsedate_to_datetime(s)
    except Exception:
        try: d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception: return now
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)

def load(name, url, tier, filt):
    out = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (news-reader)"})
        root = ET.fromstring(urllib.request.urlopen(req, timeout=20).read())
    except Exception as e:
        print("FAIL", name, e); return out
    for it in root.iter():
        if it.tag.split("}")[-1] not in ("item", "entry"): continue
        f = {}
        for c in it:
            k = c.tag.split("}")[-1]
            if k == "link" and c.get("href"): f["link"] = c.get("href")
            elif c.text and k not in f: f[k] = c.text
        title = clean(f.get("title")); link = f.get("link", "").strip()
        summ = clean(f.get("description") or f.get("summary") or f.get("encoded") or "")[:600]
        if not title or not link: continue
        if filt and not KEY.search(title + " " + summ): continue
        d = parse_date(f.get("pubDate") or f.get("published") or f.get("updated") or f.get("date") or "")
        if now - d > timedelta(days=3): continue
        out.append(dict(title=title, summary=summ, link=link, source=name, tier=tier, date=d.isoformat()))
    return out[:15]

items, seen = [], set()
for fd in FEEDS:
    for a in load(*fd):
        k = re.sub(r"\W+", "", a["title"].lower())
        if k not in seen: seen.add(k); items.append(a)
items.sort(key=lambda a: a["date"], reverse=True); items = items[:80]

def toks(a): return {w for w in re.findall(r"[a-z]{4,}", (a["title"]+" "+a["summary"]).lower()) if w not in STOP}
T = [toks(a) for a in items]
for i, a in enumerate(items):
    sc = []
    for j in range(len(items)):
        if i != j and T[i] and T[j]:
            s = len(T[i] & T[j]) / math.sqrt(len(T[i]) * len(T[j]))
            if s > 0.1: sc.append((s, j))
    a["id"] = i; a["related"] = [j for _, j in sorted(sc, reverse=True)[:4]]

json.dump(dict(updated=now.isoformat(), items=items), open("news.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(items), "articles")
