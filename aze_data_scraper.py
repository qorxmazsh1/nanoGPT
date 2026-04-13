import requests
from bs4 import BeautifulSoup
import time
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def wikipedia_article(title):
    url = f"https://az.wikipedia.org/wiki/{title.replace(' ', '_')}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        content = soup.find('div', {'id': 'mw-content-text'})
        if not content:
            return ""
        for tag in content.find_all(['table', 'sup', 'style', 'script']):
            tag.decompose()
        paragraphs = content.find_all('p')
        text = '\n'.join([p.get_text() for p in paragraphs if len(p.get_text()) > 50])
        return clean_text(text)
    except Exception as e:
        print(f"wikipedia error {title}: {e}")
        return ""

def wikipedia_random(count=100):
    texts = []
    print(f"fetching {count} articles from wikipedia")
    for i in range(count):
        try:
            r = requests.get(
                "https://az.wikipedia.org/wiki/Xüsusi:Təsadüfi_məqalə",
                headers=HEADERS, timeout=10, allow_redirects=True
            )
            soup = BeautifulSoup(r.text, 'html.parser')
            title = soup.find('h1', {'id': 'firstHeading'})
            title_text = title.get_text() if title else "?"
            content = soup.find('div', {'id': 'mw-content-text'})
            if content:
                for tag in content.find_all(['table', 'sup', 'style', 'script']):
                    tag.decompose()
                paragraphs = content.find_all('p')
                text = '\n'.join([p.get_text() for p in paragraphs if len(p.get_text()) > 50])
                text = clean_text(text)
                if len(text) > 100:
                    texts.append(text)
                    print(f"  [{i+1}/{count}] {title_text[:50]}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  [{i+1}] error: {e}")
    return texts

def azertag_news(page_count=5):
    texts = []
    print(f"fetching {page_count} pages from azertag.az")
    for page in range(1, page_count + 1):
        try:
            r = requests.get(
                f"https://azertag.az/az/xeber/page/{page}",
                headers=HEADERS, timeout=10
            )
            soup = BeautifulSoup(r.text, 'html.parser')
            links = soup.select('a[href]')
            news_links = list(set([
                ("https://azertag.az" + l.get('href')) if l.get('href', '').startswith('/') else l.get('href')
                for l in links if '/xeber/' in str(l.get('href', ''))
            ]))
            for link in news_links[:10]:
                try:
                    r2 = requests.get(link, headers=HEADERS, timeout=10)
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    paragraphs = soup2.find_all('p')
                    text = '\n'.join([p.get_text() for p in paragraphs if len(p.get_text()) > 40])
                    text = clean_text(text)
                    if len(text) > 200:
                        texts.append(text)
                        print(f"  ok: {link[:60]}")
                    time.sleep(0.3)
                except:
                    pass
        except Exception as e:
            print(f"  page {page} error: {e}")
        time.sleep(1)
    return texts

def reportaz_news(page_count=5):
    texts = []
    print(f"fetching {page_count} pages from report.az")
    for page in range(1, page_count + 1):
        try:
            r = requests.get(
                f"https://report.az/az/page/{page}/",
                headers=HEADERS, timeout=10
            )
            soup = BeautifulSoup(r.text, 'html.parser')
            links = soup.select('a[href]')
            news_links = list(set([
                l.get('href') for l in links
                if 'report.az/az/' in str(l.get('href', ''))
                and len(str(l.get('href', ''))) > 30
            ]))
            for link in news_links[:10]:
                try:
                    r2 = requests.get(link, headers=HEADERS, timeout=10)
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    paragraphs = soup2.find_all('p')
                    text = '\n'.join([p.get_text() for p in paragraphs if len(p.get_text()) > 40])
                    text = clean_text(text)
                    if len(text) > 200:
                        texts.append(text)
                        print(f"  ok: {link[:60]}")
                    time.sleep(0.3)
                except:
                    pass
        except Exception as e:
            print(f"  page {page} error: {e}")
        time.sleep(1)
    return texts

def oxuaz_news(page_count=5):
    texts = []
    print(f"fetching {page_count} pages from oxu.az")
    for page in range(1, page_count + 1):
        try:
            r = requests.get(
                f"https://oxu.az/page/{page}",
                headers=HEADERS, timeout=10
            )
            soup = BeautifulSoup(r.text, 'html.parser')
            links = soup.select('a[href*="/"]')
            news_links = list(set([
                l.get('href') for l in links
                if l.get('href') and 'oxu.az' in str(l.get('href'))
                and any(x in str(l.get('href')) for x in ['/az/', '/xeber/'])
            ]))
            for link in news_links[:10]:
                try:
                    r2 = requests.get(link, headers=HEADERS, timeout=10)
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    article = soup2.find('div', class_=re.compile(r'article|content|news|text', re.I))
                    if article:
                        text = clean_text(article.get_text())
                        if len(text) > 200:
                            texts.append(text)
                            print(f"  ok: {link[:60]}")
                    time.sleep(0.3)
                except:
                    pass
        except Exception as e:
            print(f"  page {page} error: {e}")
        time.sleep(1)
    return texts

def main():
    all_texts = []

    titles = [
        "Azərbaycan", "Bakı", "Azərbaycan_dili", "Azərbaycan_tarixi",
        "İlham_Əliyev", "Heydər_Əliyev", "Azərbaycan_mədəniyyəti",
        "Azərbaycan_iqtisadiyyatı", "Xəzər_dənizi", "Qarabağ",
        "Azərbaycan_əlifbası", "Azərbaycan_ədəbiyyatı", "Nizami_Gəncəvi",
    ]

    print("fetching articles...")
    for title in titles:
        text = wikipedia_article(title)
        if text:
            all_texts.append(text)
            print(f"  ok: {title}")
        time.sleep(0.5)

    all_texts.extend(wikipedia_random(count=100))
    all_texts.extend(azertag_news(page_count=10))
    all_texts.extend(reportaz_news(page_count=10))
    all_texts.extend(oxuaz_news(page_count=10))

    final_text = '\n\n'.join(all_texts)

    with open('az_data.txt', 'w', encoding='utf-8') as f:
        f.write(final_text)

    print(f"article count: {len(all_texts)}")
    print(f"character count: {len(final_text):,}")
    print(f"word count: {len(final_text.split()):,}")

if __name__ == "__main__":
    main()