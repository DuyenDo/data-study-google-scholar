import scrapy
from scrapy.http import TextResponse

from selenium import webdriver

import os
import sys
import time

import pandas as pd

from utils.tools import get_path, write_csv, write_pickle, monitor_crawler

class GSSpider(scrapy.Spider):
    name = "authors"

    def __init__(self):
        self.ROOT_DIR = os.path.dirname(sys.modules['__main__'].__file__)

    def start_requests(self):
        
        organizations_path = get_path([self.ROOT_DIR, "data", "organizations.txt"])
        organizations_df = pd.read_csv(organizations_path)
        urls = organizations_df['URL'].to_list()

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Configure webdriver
        chromedriver_path = get_path([self.ROOT_DIR, "libs", "chromedriver.exe"])
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=op)
        self.driver.implicitly_wait(60)

        # Extract organization id
        org_id = response.url.split("org=")[1].split("&")[0]

        # List of authors of the organization
        authors = []
        monitor_url = ''

        # Make request
        self.driver.get(response.url)

        # First page of the request
        page_response = TextResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')

        self.parse_one_page(page_response, authors)

        # Click 'Next page' and parse until this button is disabled
        while True:
            try:
                # Wait 15s before next click
                time.sleep(15)
                # Find button 'Next' when it is not hidden
                self.driver.find_element_by_xpath("//div[@id='gsc_authors_bottom_pag']//button[@aria-label='Next'][not(@disabled)]").click()
                # Create a variable for response from webdriver
                next_page_response = TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')
                self.parse_one_page(next_page_response, authors)
                
                monitor_url = self.driver.current_url
            except:
                self.driver.close()
                break

        # Output
        if len(authors) > 0:
            csv_path = get_path([self.ROOT_DIR, "data", "authors", "authors_orgID_{}.csv".format(org_id)])
            write_csv(authors, csv_path)
            
            pkl_path = get_path([self.ROOT_DIR, "data", "authors", "authors_orgID_{}.pkl".format(org_id)])
            write_pickle(authors, pkl_path)
            
            monitor_file = get_path([self.ROOT_DIR, "data", "monitors", 'crawled_organizations.txt'])
            monitor_crawler(monitor_file, monitor_url)

    def parse_one_page(self, page_response, author_list):

        rows = page_response.xpath("//div[@class='gs_ai_t']")

        if len(rows) > 0:
            for row in rows:
                author_id = row.xpath(".//h3[@class='gs_ai_name']/a/@href").get().split("user=")[1].split("&")[0]
                author_name = row.xpath(".//h3[@class='gs_ai_name']/a/text()").get()
                cited_by_str = row.xpath(".//div[@class='gs_ai_cby']/text()").get().replace("Cited by ", "")
                cited_by_int = int(cited_by_str) if cited_by_str.isdigit() else 0
                
                author = {
                    'AuthorID': author_id,
                    'AuthorName': author_name,
                    'Count_cited': cited_by_int
                }

                author_list.append(author)