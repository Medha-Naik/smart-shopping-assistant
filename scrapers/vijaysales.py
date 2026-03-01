from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def scrape_vijaysales(product_name):
    search_query = product_name.replace(' ', '+')
    url = f"https://www.vijaysales.com/search/{search_query}"
    print(f"Searching: {url}\n")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(8)

        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # after soup is created, add this temporarily
        print(soup.find_all('div', class_=lambda c: c and 'product' in c.lower())[:3])
        products = soup.find_all('div', {'class': 'product-card'})
        print(f"Found {len(products)} products")

        data = []
        for product in products:
            image = product.find('img', {'class': 'product__image'})
            link = product.find('a', {'class': 'product-card__link'})
            name = product.find('div', {'class': 'product-name'})
            price_div = product.find('div', {'class': 'discountedPrice'})
            price = price_div['data-price'] if price_div else None

            if name and price:
                data.append({
                    'name': name.text.strip(),
                    'price': '₹' + price,
                    'rating': 'N/A',
                    'image': image['src'] if image else None,
                    'url': 'https://www.vijaysales.com' + link['href'] if link else 'N/A'
                })

        return data

    except Exception as e:
        print(f"Error: {e}")
        return []

    finally:
        driver.quit()


if __name__ == '__main__':
    results = scrape_vijaysales('iphone 15')
    for r in results:
        print(r)