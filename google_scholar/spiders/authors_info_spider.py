import scrapy
from scrapy.http import TextResponse

from selenium import webdriver

import time
import os
import sys
import platform

import csv

import pandas as pd

from utils.tools import get_path, write_csv, write_pickle, monitor_crawler


class GSSpider(scrapy.Spider):
    name = "info"

    def __init__(self, author_file=''):
        self.ROOT_DIR = os.path.dirname(sys.modules['__main__'].__file__)
        self.author_file = author_file

    def start_requests(self):
        # URLs of users

        authors_path = get_path(
            [self.ROOT_DIR, "data", "authors", self.author_file])
        authors_df = pd.read_csv(authors_path)

        urls = ('https://scholar.google.com/citations?hl=en&user=' + authors_df['AuthorID'].astype(str))\
                .to_list()

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Configure webdriver
        if platform.system() == 'Windows':
            chromedriver_path = get_path(
                [self.ROOT_DIR, "libs", "chromedriver.exe"])
        else:
            chromedriver_path = get_path(
                [self.ROOT_DIR, "libs", "chromedriver"])
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        self.driver = webdriver.Chrome(
            executable_path=chromedriver_path, options=op)
        self.driver.implicitly_wait(60)

        # Get user_id from URL
        user_id = response.url.split("user=")[1].split("&")[0]

        # Make request
        self.driver.get(response.url)

        info_tags = response.xpath(
            "//div[@id='gsc_prf_i']//div[@class='gsc_prf_il']")
        info_texts = info_tags.xpath(".//text()").getall()
        info_links = info_tags.xpath(".//a/@href").getall()

        info_texts_str = " | ".join(info_texts)
        info_links_str = " | ".join(info_links)

       # Get all rows in the table from webdriver response, each paper is in a row
        rows = response.xpath(
            "//table[@id='gsc_rsb_st']//tbody//td[@class='gsc_rsb_std']")

        citations_all = int(rows[0].xpath("text()").get()) if rows[0].xpath("text()").get() is not None else 0
        citations_s2014 = int(rows[1].xpath("text()").get()) if rows[0].xpath("text()").get() is not None else 0
        hindex_all = int(rows[2].xpath("text()").get()) if rows[0].xpath("text()").get() is not None else 0
        hindex_s2014 = int(rows[3].xpath("text()").get()) if rows[0].xpath("text()").get() is not None else 0
        i10index_all = int(rows[4].xpath("text()").get()) if rows[0].xpath("text()").get() is not None else 0
        i10index_s2014 = int(rows[5].xpath("text()").get()) if rows[0].xpath("text()").get() is not None else 0

        coauthor_ids = ''
        coauthor_names = ''
        try:
            self.driver.find_element_by_xpath("//button[@id='gsc_coauth_opn']").click()
            coauthors_response = TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')
            (coauthor_ids, coauthor_names) = self.parse_coauthors(coauthors_response)
        except:
            pass
        
        info = {
            "AuthorID": user_id,
            "CitationsAll": citations_all,
            "CitationsS2014": citations_s2014,
            "hIndexAll": hindex_all,
            "hIndexS2014": hindex_s2014,
            "i10IndexAll": i10index_all,
            "i10IndexS2014": i10index_s2014,
            "CoAuthorIDs": coauthor_ids,
            "CoAuthorNames": coauthor_names,
            "Description": info_texts_str,
            "DescriptionURLs": info_links_str
        }
        
        # Output
        csv_path = get_path([self.ROOT_DIR, "data", "info", "info-{}.csv".format(self.author_file.split(".")[0])])
        write_csv([info], csv_path)
        pkl_path = get_path([self.ROOT_DIR, "data", "info", "info-{}.pkl".format(self.author_file.split(".")[0])])
        write_pickle([info], pkl_path)

        monitor_file = get_path([self.ROOT_DIR, "data", "monitors", 'crawled_info_{}'.format(self.author_file)])
        monitor_crawler(monitor_file, user_id)

        self.driver.close()

        time.sleep(30)
    
    def parse_coauthors(self, response):
        rows = response.xpath("//div[@id='gsc_codb_content']//h3[@class='gs_ai_name']")
        coauthor_id_list = []
        coauthor_name_list = []
        for row in rows:
            coauthor_id = row.xpath("./a/@href").get().split('user=')[1].split('&')[0]
            coauthor_name = row.xpath("./a/text()").get()
            coauthor_id_list.append(coauthor_id)
            coauthor_name_list.append(coauthor_name)
        
        coauthor_ids = ", ".join(coauthor_id_list)
        coauthor_names = ", ".join(coauthor_name_list)
        return (coauthor_ids, coauthor_names)


