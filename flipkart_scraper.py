from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def scrape_flipkart(product_name):
    search_query = product_name.replace(' ', '+')
    url = f"https://www.flipkart.com/search?q={search_query}"

    print(f"Searching: {url}\n")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # runs chrome in background, no window opens
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')


    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(3)  # wait for page to load

        soup = BeautifulSoup(driver.page_source, 'html.parser')
       


        products = soup.find_all('div', {'class': 'ZFwe0M'})
        print(f"Found {len(products)} products")
        
        data = []

        


        for product in products:
            parent_container = product.find_parent('div',attrs={'data-id':True})
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
        driver.quit()  # always close the browser


    