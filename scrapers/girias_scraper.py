from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
import re

BASE_URL = "https://www.giriasindia.com"


def scrape_girias(product_name):
    search_query = product_name.replace(' ', '+')
    url = f"{BASE_URL}/search?q={search_query}"
    print(f"Searching: {url}\n")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(6)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = soup.find_all('a', href=re.compile(r'^/product/'))
        print(f"Found {len(products)} products")

        data = []

        for product in products:
            name = product.find('h4', class_=re.compile(r'truncate'))
            price = product.find('div', class_=lambda c: c and 'font-semibold' in c and 'text-xl' in c)
            image = product.find('img')

            if name and price:
                img_src = image.get('src') or image.get('data-src') if image else 'N/A'
                if img_src and not img_src.startswith('http'):
                    img_src = urljoin(BASE_URL, img_src)

                data.append({
                    'name': re.sub(r'-\d{4,6}$', '', name.get_text(strip=True)).strip(),
                    'price': price.get_text(separator='', strip=True),
                    'rating': 'N/A',
                    'image': img_src or 'N/A',
                    'url': urljoin(BASE_URL, product.get('href', '')),
                    'source': 'Girias'
                })

        return data

    except Exception as e:
        print(f"Error: {e}")
        return []

    finally:
        driver.quit()


def girias_price(url):
    parsed = urlparse(url)
    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(clean_url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        price_el = soup.find('div', class_='font-bold text-2xl')

        text = ''.join(price_el.stripped_strings)
        if price_el:
            price_str = re.sub(r'[₹,\s]', '', price_el.get_text(separator='', strip=True))
            try:
                return float(price_str)
                
            except ValueError:
                return None

        return None

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        driver.quit()

