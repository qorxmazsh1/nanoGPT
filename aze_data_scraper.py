import requests
from bs4 import BeautifulSoup
import time
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def temizle(metn):
    metn = re.sub(r'\s+', ' ', metn)
    metn = metn.strip()
    return metn

def vikipediya_meqale(baslig):
    url = f"https://az.wikipedia.org/wiki/{baslig.replace(' ', '_')}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        content = soup.find('div', {'id': 'mw-content-text'})
        if not content:
            return ""
        for tag in content.find_all(['table', 'sup', 'style', 'script']):
            tag.decompose()
        paragraflar = content.find_all('p')
        metn = '\n'.join([p.get_text() for p in paragraflar if len(p.get_text()) > 50])
        return temizle(metn)
    except Exception as e:
        print(f"vikipediya xetasi {baslig}: {e}")
        return ""

def vikipediya_random(sayi=100):
    metinler = []
    print(f"vikipediyadan {sayi} meqale cekilir")
    for i in range(sayi):
        try:
            r = requests.get(
                "https://az.wikipedia.org/wiki/Xüsusi:Təsadüfi_məqalə",
                headers=HEADERS, timeout=10, allow_redirects=True
            )
            soup = BeautifulSoup(r.text, 'html.parser')
            baslig = soup.find('h1', {'id': 'firstHeading'})
            baslig_metn = baslig.get_text() if baslig else "?"
            content = soup.find('div', {'id': 'mw-content-text'})
            if content:
                for tag in content.find_all(['table', 'sup', 'style', 'script']):
                    tag.decompose()
                paragraflar = content.find_all('p')
                metn = '\n'.join([p.get_text() for p in paragraflar if len(p.get_text()) > 50])
                metn = temizle(metn)
                if len(metn) > 100:
                    metinler.append(metn)
                    print(f"  [{i+1}/{sayi}] {baslig_metn[:50]}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  [{i+1}] xeta: {e}")
    return metinler

def azertag_xeberler(sehife_sayi=5):
    metinler = []
    print(f"azertag.az den {sehife_sayi} sehife cekilir")
    for sehife in range(1, sehife_sayi + 1):
        try:
            r = requests.get(
                f"https://azertag.az/az/xeber/page/{sehife}",
                headers=HEADERS, timeout=10
            )
            soup = BeautifulSoup(r.text, 'html.parser')
            links = soup.select('a[href]')
            xeber_linkler = list(set([
                ("https://azertag.az" + l.get('href')) if l.get('href', '').startswith('/') else l.get('href')
                for l in links if '/xeber/' in str(l.get('href', ''))
            ]))
            for link in xeber_linkler[:10]:
                try:
                    r2 = requests.get(link, headers=HEADERS, timeout=10)
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    paragraflar = soup2.find_all('p')
                    metn = '\n'.join([p.get_text() for p in paragraflar if len(p.get_text()) > 40])
                    metn = temizle(metn)
                    if len(metn) > 200:
                        metinler.append(metn)
                        print(f"  ok: {link[:60]}")
                    time.sleep(0.3)
                except:
                    pass
        except Exception as e:
            print(f"  sehife {sehife} xetasi: {e}")
        time.sleep(1)
    return metinler

def reportaz_xeberler(sehife_sayi=5):
    metinler = []
    print(f"report.az den {sehife_sayi} sehife cekilir")
    for sehife in range(1, sehife_sayi + 1):
        try:
            r = requests.get(
                f"https://report.az/az/page/{sehife}/",
                headers=HEADERS, timeout=10
            )
            soup = BeautifulSoup(r.text, 'html.parser')
            links = soup.select('a[href]')
            xeber_linkler = list(set([
                l.get('href') for l in links
                if 'report.az/az/' in str(l.get('href', ''))
                and len(str(l.get('href', ''))) > 30
            ]))
            for link in xeber_linkler[:10]:
                try:
                    r2 = requests.get(link, headers=HEADERS, timeout=10)
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    paragraflar = soup2.find_all('p')
                    metn = '\n'.join([p.get_text() for p in paragraflar if len(p.get_text()) > 40])
                    metn = temizle(metn)
                    if len(metn) > 200:
                        metinler.append(metn)
                        print(f"  ok: {link[:60]}")
                    time.sleep(0.3)
                except:
                    pass
        except Exception as e:
            print(f"  sehife {sehife} xetasi: {e}")
        time.sleep(1)
    return metinler

def oxuaz_xeberler(sehife_sayi=5):
    metinler = []
    print(f"oxu.az den {sehife_sayi} sehife cekilir")
    for sehife in range(1, sehife_sayi + 1):
        try:
            r = requests.get(
                f"https://oxu.az/page/{sehife}",
                headers=HEADERS, timeout=10
            )
            soup = BeautifulSoup(r.text, 'html.parser')
            links = soup.select('a[href*="/"]')
            xeber_linkler = list(set([
                l.get('href') for l in links
                if l.get('href') and 'oxu.az' in str(l.get('href'))
                and any(x in str(l.get('href')) for x in ['/az/', '/xeber/'])
            ]))
            for link in xeber_linkler[:10]:
                try:
                    r2 = requests.get(link, headers=HEADERS, timeout=10)
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    article = soup2.find('div', class_=re.compile(r'article|content|news|text', re.I))
                    if article:
                        metn = temizle(article.get_text())
                        if len(metn) > 200:
                            metinler.append(metn)
                            print(f"  ok: {link[:60]}")
                    time.sleep(0.3)
                except:
                    pass
        except Exception as e:
            print(f"  sehife {sehife} xetasi: {e}")
        time.sleep(1)
    return metinler

def main():
    butun_metinler = []

    basliglar = [
        "Azərbaycan", "Bakı", "Azərbaycan_dili", "Azərbaycan_tarixi",
        "İlham_Əliyev", "Heydər_Əliyev", "Azərbaycan_mədəniyyəti",
        "Azərbaycan_iqtisadiyyatı", "Xəzər_dənizi", "Qarabağ",
        "Azərbaycan_əlifbası", "Azərbaycan_ədəbiyyatı", "Nizami_Gəncəvi",
    ]

    print("meqaleler cekilir...")
    for baslig in basliglar:
        metn = vikipediya_meqale(baslig)
        if metn:
            butun_metinler.append(metn)
            print(f"  ok: {baslig}")
        time.sleep(0.5)

    butun_metinler.extend(vikipediya_random(sayi=100))
    butun_metinler.extend(azertag_xeberler(sehife_sayi=10))
    butun_metinler.extend(reportaz_xeberler(sehife_sayi=10))
    butun_metinler.extend(oxuaz_xeberler(sehife_sayi=10))

    yekun_metn = '\n\n'.join(butun_metinler)

    with open('az_data.txt', 'w', encoding='utf-8') as f:
        f.write(yekun_metn)

    print(f"meqale sayi: {len(butun_metinler)}")
    print(f"simvol sayi: {len(yekun_metn):,}")
    print(f"söz sayi: {len(yekun_metn.split()):,}")

if __name__ == "__main__":
    main()