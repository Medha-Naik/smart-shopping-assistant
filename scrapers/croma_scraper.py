from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def scrape_croma(product_name):
    search_query = product_name.replace(' ', '+')
    url = f"https://www.croma.com/searchB?q={search_query}"
    print(f"Searching: {url}\n")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(5)

        with open('debug.html','w',encoding='utf-8')as f:
            f.write(driver.page_source)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = soup.find_all('li', {'class': 'product-item'})
        print(f"Found {len(products)} products")

        data = []
        for product in products:
            image = product.find('img')
            link = product.find('a', {'class': 'product-title'})  # the anchor wrapping the title
            name = product.find('h3', {'class': 'product-title'})
            price = product.find('span', {'class': 'amount'})
            rating = product.find('div', {'class': 'cp-rating'})

            if name and price:
                data.append({
                    'name': name.text.strip(),
                    'price': price.text.strip(),
                    'rating': rating.text.strip() if rating else 'N/A',
                    'image': image['data-src'] if image and image.get('data-src') else None,
                    'url': 'https://www.croma.com' + link['href'] if link else 'N/A'
                })

        return data

    except Exception as e:
        print(f"Error: {e}")
        return []

    finally:
        driver.quit()


if __name__ == '__main__':
    results = scrape_croma('iphone 15')
    for r in results:
        print(r)