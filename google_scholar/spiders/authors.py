import scrapy
from scrapy.http import TextResponse
from selenium import webdriver
import os
import csv
import logging
import time

logging.basicConfig(filename=os.path.join(os.path.dirname(__file__), '..\\..\\logs\\authors.log'),\
                    level=logging.ERROR)
logger = logging.getLogger(__name__)

class GSSpider(scrapy.Spider):
    name = "authors"

    def start_requests(self):
        # Get authors verified by the given email domain name
        urls = [
            # 'https://scholar.google.com/citations?hl=en&view_op=search_authors&mauthors=%s' % 'eurecom.fr',
            "https://scholar.google.com/citations?view_op=view_org&hl=en&org=8539678734835078480&fbclid=IwAR0AN_dLcYIL4IW5XspJ_BjnrI91SYQ3RIWiUi8agVL0X7ZAeKiXxOmSyCU"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        # Path to chromedriver.exe
        chromedriver_path = os.path.join(os.path.dirname(__file__), '..\\..\\libs\\chromedriver.exe')
        # Create a webdriver
        self.driver = webdriver.Chrome(chromedriver_path)
        # Wait 60 seconds for loading page if the element is not available yet
        self.driver.implicitly_wait(60)

        # Tracking the current url
        current_url = response.url

        # Create a list of authors who are verified by the given email domain name
        authors = []

        # Use webdriver to make request to a user's URL
        self.driver.get(response.url)

        # Create a variable for response from webdriver
        page_response = TextResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')

        self.parse_one_page(page_response, authors)

        # Click 'Next page' until this button is disabled
        while True:
            try:
                # Find button 'Next' when it is not hidden
                self.driver.find_element_by_xpath("//div[@id='gsc_authors_bottom_pag']//button[@aria-label='Next'][not(@disabled)]").click()

                # Create a variable for response from webdriver
                next_page_response = TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')

                self.parse_one_page(next_page_response, authors)

                current_url = self.driver.current_url

                # Wait 60 seconds before next click
                time.sleep(15)

            except Exception as e: 
                logger.info(current_url)
                logger.error(e)

                # Close webdriver
                self.driver.close()
                break

        data_folder = os.path.join(os.path.dirname(__file__), '..\\..\\data\\')
        # Create a filename
        file_cited_papers = '%sauthors_list-%s.csv' % (data_folder, 'standford_2')
        # Write list of papers to csv file
        keys = authors[0].keys()
        with open(file_cited_papers, 'w', encoding='utf-8', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(authors)

    
    def parse_one_page(self, page_response, author_list):

        rows = page_response.xpath("//div[@class='gs_ai_t']")

        for row in rows:
            author_id = row.xpath(".//h3[@class='gs_ai_name']/a/@href").get()\
                            .split("user=")[1].split("&")[0]
            author_name = row.xpath(".//h3[@class='gs_ai_name']/a/text()").get()
            cited_by_str = row.xpath(".//div[@class='gs_ai_cby']/text()").get()\
                            .replace("Cited by ", "")
            cited_by_int = int(cited_by_str) if cited_by_str.isdigit() else 0
            # Create a dictionary for each paper
            
            author = {
                'AuthorID': author_id,
                'AuthorName': author_name,
                'Count_cited': cited_by_int
            }

            author_list.append(author)