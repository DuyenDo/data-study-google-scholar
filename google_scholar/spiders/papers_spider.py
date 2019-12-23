import scrapy
from scrapy.http import TextResponse
from scrapy.utils.log import configure_logging

from selenium import webdriver

import time
import os
import sys

import csv

import pandas as pd

from utils.tools import get_path, write_csv, write_pickle, monitor_crawler

class GSSpider(scrapy.Spider):
    name = "papers_2"

    def __init__(self, input_file = ''):
        self.ROOT_DIR = os.path.dirname(sys.modules['__main__'].__file__)
        self.input_file = input_file

    def start_requests(self):
        authors_path = get_path([self.ROOT_DIR, "data", "authors", self.input_file])
        authors_df = pd.read_csv(authors_path)
        
        urls = ('https://scholar.google.com/citations?hl=en&user=' + authors_df['AuthorID'].astype(str))\
                .to_list()[0:1]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Configure webdriver
        chromedriver_path = get_path([self.ROOT_DIR, "libs", "chromedriver.exe"])
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=op)
        self.driver.implicitly_wait(60)
        
        # Extract user_id
        user_id = response.url.split("user=")[1].split("&")[0]
        
        # Make request
        self.driver.get(response.url)

        response_after_click = None

        # Click 'Show more' until the button is disabled
        while True:
            try:
                # Wait 15 seconds before next click
                time.sleep(15)
                # Click button 'Show more' while it is not disabled
                self.driver.find_element_by_xpath('//button[@id="gsc_bpf_more"][not(@disabled)]').click()
            except:
                # Get response after clicking completely
                response_after_click = TextResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')
                # Close webdriver
                self.driver.close()
                break

        # Create a list of papers for the given user
        papers = []

        # Get all rows in the table from webdriver response, each paper is in a row
        rows = response_after_click.xpath("//table[@id='gsc_a_t']//tr[@class='gsc_a_tr']")

        if (len(rows)>0):
            # In each paper, get title, authors, conference, url of citations, count of citations and year of publication
            for row in rows:
                title = row.xpath(".//td[@class='gsc_a_t']/a/text()").get()
                authors = row.xpath(".//td[@class='gsc_a_t']/div[1]/text()").get()
                conference = row.xpath(".//td[@class='gsc_a_t']/div[2]/text()").get()
                cited_url = row.xpath(".//td[@class='gsc_a_c']/a[@class='gsc_a_ac gs_ibl']/@href").get()
                cited_count = row.xpath(".//td[@class='gsc_a_c']/a/text()").get()
                year = row.xpath(".//td[@class='gsc_a_y']/span/text()").get()

                cited_count = 0 if cited_count is None else int(cited_count)
                year = 0 if year is None else int(year)

                # Create a dictionary for each paper
                paper = {
                    'Title': title,
                    'Authors': authors,
                    'Platform': conference,
                    'Cited_url': cited_url,
                    'Cited_count': cited_count,
                    'Year': year
                }

                papers.append(paper)
            
            # Output
            organization = self.input_file.split('.')[0].replace("authors_", "")
            papers_csv = get_path([self.ROOT_DIR,\
                                "data", "papers", organization, "papers-of-authorID-{}.csv".format(user_id)])
            write_csv(papers, papers_csv)
            papers_pkl = get_path([self.ROOT_DIR, \
                                "data", "papers", organization, "papers-of-authorID-{}.pkl".format(user_id)])
            write_pickle(papers, papers_pkl)
            monitor_file = get_path([self.ROOT_DIR, "data", "monitors", 'crawled_' + self.input_file])
            monitor_crawler(monitor_file, user_id)