from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
import re

BASE_URL = "https://www.giriasindia.com"


def _make_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def _clean_price(text):
    if not text:
        return None
    cleaned = re.sub(r'[^\d.]', '', text)
    try:
        return float(cleaned)
    except ValueError:
        return None


def _has_classes(tag, *classes):
    tag_classes = set(tag.get('class', []))
    return all(c in tag_classes for c in classes)


def scrape_girias(product_name):
    query_encoded = product_name.replace(' ', '+')
    search_url = f"{BASE_URL}/search?q={query_encoded}"
    print(f"[Girias] Searching: {search_url}")

    driver = _make_driver()
    try:
        driver.get(search_url)
        try:
            WebDriverWait(driver, 12).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/product/"]'))
            )
        except Exception:
            time.sleep(6)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return _parse_search_results(soup)

    except Exception as e:
        print(f"[Girias] Scrape error: {e}")
        return []
    finally:
        driver.quit()


def _parse_search_results(soup):
    
    results = []
    seen = set()

    product_anchors = soup.find_all('a', href=re.compile(r'^/product/'))

    for anchor in product_anchors:
        href = anchor.get('href', '')
        full_url = urljoin(BASE_URL, href)
        if full_url in seen:
            continue
        seen.add(full_url)

        # ── Name: <h4 class='text-sm uppercase truncate text-center mb-2'> ──
        name_el = anchor.find('h4', class_=re.compile(r'truncate'))
        name = name_el.get_text(strip=True) if name_el else None

        # Fallback: any h4 inside anchor
        if not name:
            h4 = anchor.find('h4')
            name = h4.get_text(strip=True) if h4 else None

        # Strip trailing SKU code e.g. "-28711"
        if name:
            name = re.sub(r'-\d{4,6}$', '', name).strip()

        if not name or len(name) < 4:
            continue

        # ── Price: <div class='font-semibold text-xl text-center'> ──
        # Contains two text nodes: "₹" and "82,900" → joined = "₹82,900"
        price_text = 'N/A'
        for div in anchor.find_all('div'):
            if _has_classes(div, 'font-semibold', 'text-xl'):
                raw = div.get_text(separator='', strip=True)
                if raw:
                    price_text = raw
                break

        # ── Image: inside <div class='relative h-36 mb-4'> ──
        img_el = anchor.find('img')
        image = 'N/A'
        if img_el:
            image = img_el.get('src') or img_el.get('data-src') or 'N/A'
            if image and not image.startswith('http'):
                image = urljoin(BASE_URL, image)

        results.append({
            'name': name,
            'price': price_text,
            'rating': 'N/A',
            'image': image,
            'url': full_url,
            'source': 'Girias'
        })

    print(f"[Girias] Found {len(results)} products")
    return results


def scrape_girias_price_by_url(url):
    """
    Product detail page price.
    DevTools confirmed: <div class='font-bold text-2xl'> with ₹ + number as child text nodes.
    """
    parsed = urlparse(url)
    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    driver = _make_driver()
    try:
        driver.get(clean_url)
        try:
            WebDriverWait(driver, 12).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))
            )
        except Exception:
            time.sleep(6)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Detail page: <div class='font-bold text-2xl'>
        for div in soup.find_all('div'):
            if _has_classes(div, 'font-bold', 'text-2xl'):
                raw = div.get_text(separator='', strip=True)
                price = _clean_price(raw)
                if price and price > 100:
                    return price

        # Fallback: scan text nodes
        for el in soup.find_all(string=re.compile(r'₹[\d,]+')):
            price = _clean_price(el)
            if price and price > 100:
                return price

        return None

    except Exception as e:
        print(f"[Girias] Price check error: {e}")
        return None
    finally:
        driver.quit()

