from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import re

def scrape_flipkart(product_name):
    search_query = product_name.replace(' ', '+')
    url = f"https://www.flipkart.com/search?q={search_query}"
    print(f"Searching: {url}\n")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = soup.find_all('div', {'class': 'ZFwe0M'})
        print(f"Found {len(products)} products")

        data = []

        for product in products:
            parent_container = product.find_parent('div', attrs={'data-id': True})
            image = parent_container.find('img', {'class': 'UCc1lI'}) if parent_container else None
            link = parent_container.find('a', {'class': 'k7wcnx'}) if parent_container else None

            name = product.find('div', {'class': 'RG5Slk'})
            price = product.find('div', {'class': 'hZ3P6w'})
            rating = product.find('div', {'class': 'MKiFS6'})

            if name and price:
                data.append({
                    'name': name.text.strip(),
                    'price': price.text.strip(),
                    'rating': rating.text.strip() if rating else 'N/A',
                    'image': image['src'] if image else 'N/A',
                    'url': 'https://www.flipkart.com' + link['href'] if link else 'N/A'
                })

        return data

    except Exception as e:
        print(f"Error: {e}")
        return []

    finally:
        driver.quit()


def scrape_price_by_url(url):
    # Clean URL - remove tracking parameters
    parsed = urlparse(url)
    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')


        candidates=soup.find_all('div',class_=['v1zwn21k', 'v1zwn20', '_1psv1zeb9', '_1psv1ze0'])
        for el in candidates:
            text=el.text.strip()
            if text.startswith('₹'):
                price_str = re.sub(r'[₹,\s]', '', text)
                return float(price_str)
        
        return None

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        driver.quit()


    