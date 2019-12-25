import scrapy
from scrapy.http import TextResponse

from selenium import webdriver

import time
import os
import sys
import platform

import glob

import csv

import pandas as pd

from utils.tools import get_path, write_csv, write_pickle, monitor_crawler

class GSSpider(scrapy.Spider):
    name = "citations"

    def __init__(self, input_dir = '', input_file = ''):
        self.ROOT_DIR = os.path.dirname(sys.modules['__main__'].__file__)
        self.input_dir = input_dir
        self.input_file = input_file

    def start_requests(self):
        urls = []
        try:
            if self.input_file == '':
                path = get_path([self.ROOT_DIR, "data", "papers", self.input_dir, "*.csv"])
                for path_file in glob.glob(path):
                    df = pd.read_csv(path_file)
                    urls.extend(df['Cited_url'].dropna().to_list())
            else:
                path = get_path([self.ROOT_DIR, "data", "papers", self.input_dir, self.input_file])
                urls = pd.read_csv(path)['Cited_url'].dropna().to_list()
        except:
            raise

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Configure webdriver
        if platform.system() == 'Windows':
            chromedriver_path = get_path([self.ROOT_DIR, "libs", "chromedriver.exe"])
        else:
            chromedriver_path = get_path([self.ROOT_DIR, "libs", "chromedriver"])
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=op)
        self.driver.implicitly_wait(60)
        
        # Monitor the process by url
        monitor_url = response.url

        citation_id = response.url.split("cites=")[1].split("&")[0].replace(",", "_")

        citations = []

        # Make request, get response and extract content
        self.driver.get(response.url)
        page_response = TextResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')
        self.parse_one_page(page_response, citations)

        # Click 'Next page' and get content until this button is disabled
        while True:
            try:
                # Wait 15s before next click
                time.sleep(15)
                
                # Click button 'Next' when it is not hidden
                self.driver.find_element_by_xpath("//div[@id='gs_n']//td[@align='left']/a").click()
                
                # Get content, parse and monitor
                next_page_response = TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')
                self.parse_one_page(next_page_response, cited_by_list)
                monitor_url = self.driver.current_url
            except:
                self.driver.close()
                break

        # Output
        csv_path = get_path([self.ROOT_DIR, "data", "citations", self.input_dir, self.input_file.split(".")[0], \
                            "papers-of-citeID-{}.csv".format(citation_id)])
        write_csv(citations, csv_path)
        pkl_path = get_path([self.ROOT_DIR, "data", "citations", self.input_dir, self.input_file.split(".")[0], \
                            "papers-of-citeID-{}.pkl".format(citation_id)])
        write_pickle(citations, pkl_path)

        monitor_file = get_path([self.ROOT_DIR, "data", "monitors", "crawled_papers_{}_{}"\
                                .format(self.input_dir.replace("authors_",""), self.input_file.replace("papers-of-",""))])
        monitor_crawler(monitor_file, monitor_url)

    
    def parse_one_page(self, page_response, citations):

        rows = page_response.xpath("//div[@id='gs_res_ccl_mid']//div[@class='gs_ri']")

        # In each citation, get title of the paper, id of authors, name of authors
        if len(rows) > 0:
            for row in rows:
                title_list = row.xpath(".//h3[@class='gs_rt']//text()").getall()
                author_ids_list = row.xpath(".//div[@class='gs_a']/a/@href").getall()
                author_name_list = row.xpath(".//div[@class='gs_a']/a/text()").getall()
                cited_url = row.xpath(".//div[@class='gs_fl']/a[contains(text(),'Cited by')]/@href").get()

                # Join elements of list to text
                title = " ".join(title_list)
                author_ids = ", ".join([author_id.split("user=")[1].split("&")[0] for author_id in author_ids_list])
                author_names = ", ".join(author_name_list)

                cited_by = {
                    'Title': title,
                    'AuthorIDs': author_ids,
                    'AuthorNames': author_names,
                    'Cited_url': cited_url
                }

                citations.append(cited_by)