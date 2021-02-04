from time import sleep
import random
# Scrapy:
from scrapy.item import Item
from scrapy.item import Field
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider
# Selenium:
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait # TO WAIT INTELLIGENTLY, INSTEAD OF USING "sleep".
from selenium.webdriver.support import expected_conditions as EC
# BeautifulSoup:
from bs4 import BeautifulSoup

# SCRAPY:
# Defining the class where we will retrieve our data:
class CarProduct(Item):
    Product = Field()
    Price = Field()
    
# Defining the spider that we will use to scrape the data:
class OlxCrawlSpider(CrawlSpider):
    name = "OlxCrawlSpider"
    custom_settings = {
        "USER_AGENT":"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/84.0.2",
    }
    allowed_domains = ["olx.com.co"]
    start_urls = ["https://www.olx.com.co/items/q-autos"]
    download_delay = 1
    
    def parse_start_url(self, response):
        
        # SELENIUM (Initializing the main page):
        opts = Options()
        ua = "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/88.0.4324.96 Chrome/88.0.4324.96 Safari/537.36"
        opts.add_argument(ua) # "ua" stands for user agent.
        driver = webdriver.Chrome("./chromedriver.exe", options=opts)
        driver.get(self.start_urls[0]) # We retrieve the main/seed url to load the website.
        sleep(random.uniform(3,4)) # We wait until the main website loads everything.
        
        # LOADING THE DYNAMICALLY DATA WE WANT:
        for new_data in range(3): # We will push the button just 3 times.
            try:
                # WE USE INTELLIGENT WAIT AFTER EVERY CLICK.
                button = WebDriverWait(driver, 10).until( # We wait for the data up to 10s. Whenever the button loads we retrieve it and proceed with the code.
                    EC.presence_of_element_located((By.XPATH, "//button[@data-aut-id = 'btnLoadMore']"))
                )
                button.click() # We click on the retrieved button.
                WebDriverWait(driver, 10).until( # We wait for the elements to load after the "click()" event.
                    EC.presence_of_all_elements_located((By.XPATH, "//ul[@data-aut-id='itemsList']/li"))
                )
            except:
                print("Has llegado al final de la página.")
                break
        
        # BEAUTIFULSOUP (Obtaining and saving the data):
        sleep(random.uniform(3,4)) # THIS IS A MUST. I DON'T KNOW EXACTLY WHY, BUT IF WE DON'T WAIT A LITTLE, THE SCRAPER WON'T RETRIEVE ANYTHING.
        html_tree = driver.page_source # We retrieve the new html tree generated after the "click()" events.
        BS_object = BeautifulSoup(html_tree, 'lxml')
        containers = BS_object.find_all("li", {"data-aut-id":'itemBox'})
        for container in containers:
            product = container.find("span", {"data-aut-id":"itemTitle"}).get_text()
            price_nums = container.find("span", {"data-aut-id":"itemPrice"}).text.replace('$','').strip().split('.')
            
            # To adapt the price, since it has many points; for example, "$ 405.856.000". That's why turn this directly into "float" causes problems.
            nums = ''
            for lnum in price_nums[:-1]: # Numbers at the left side from the last point(.).
                nums += lnum
            nums += '.' # To seperate the ints from the decimal ones (for example: 10.15).
            for rnum in price_nums[-1]: # Numbers at the right side from the last point(.).
                nums += rnum
            
            price = float(nums)
            item = ItemLoader(CarProduct(), html_tree)
            item.add_value("Product", product)
            item.add_value("Price", price)

            yield item.load_item()