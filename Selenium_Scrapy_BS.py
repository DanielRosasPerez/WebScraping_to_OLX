import random, json
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
######################################################
from scrapy.item import Item
from scrapy.item import Field
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from bs4 import BeautifulSoup

class PythonProducts(Item):
    Product = Field()
    Price = Field()
    
class CrawlPythonProducts(CrawlSpider):
    name = "CrawlPythonProducts"
    custom_settings = {
        "USER_AGENT":"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/84.0.2",
        "FEED_EXPORT_ENCODING":"utf-8"
    }
    allowed_domains = ["olx.com.co"]
    start_urls = ["https://www.olx.com.co/items/q-python"]
    download_delay = 1
        
    def parse_start_url(self, response):
        
        # LET'S LOAD THE WHOLE DATA FROM THIS PAGE USING "SELENIUM".
        opts = Options()
        ua = "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/88.0.4324.96 Chrome/88.0.4324.96 Safari/537.36"
        opts.add_argument(ua) # "ua" stands for "user-agent".
        driver = webdriver.Chrome("./chromedriver.exe", options=opts)
        driver.get(self.start_urls[0]) # Main/Seed URL.
        sleep(random.uniform(3,3)) # We wait for the inital data to load normally. Otherwise, we won't be able to retrieve the new data after the "click()".
        cargar_mas = driver.find_element(By.XPATH, "//button[@data-aut-id = 'btnLoadMore']")
        cargar_mas.click() # We click on the button that loads more data.
        print("¡DYNAMICALLY DATA LOADING...!")
        sleep(random.uniform(3,3)) # We wait up to the dynamically data loads.
        print("¡DATA HAS BEEN LOADED :)!")
        sleep(1)
        html_tree = driver.page_source # We obtain the new html_tree that contains the new extra data.
        
        # ONCE ALL THE DYNAMICALLY DATA HAS BEEN LOADED, IT'S TIME TO EXTRACT DATA USING "SCRAPY":
        BS_object = BeautifulSoup(html_tree, 'lxml')
        containers = BS_object.find_all("li", {"data-aut-id":'itemBox'})
        for container in containers:
            product = container.find("span", {"data-aut-id":"itemTitle"}).get_text()
            price = float(container.find("span", {"data-aut-id":"itemPrice"}).text.replace('$','').strip())
            item = ItemLoader(PythonProducts(), html_tree)
            item.add_value("Product", product)
            item.add_value("Price", price)
            
            yield item.load_item()
        
        # MORE INFO ABOUT "WEB DRIVER": "https://www.browserstack.com/guide/get-html-source-of-web-element-in-selenium-webdriver"
            
