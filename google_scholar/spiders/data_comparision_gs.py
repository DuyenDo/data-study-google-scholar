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
    name = "data_comparison_gs"

    def __init__(self, input_file = ''):
        self.ROOT_DIR = os.path.dirname(sys.modules['__main__'].__file__)

    def start_requests(self):
        # URLs of users
        urls = [
            'https://scholar.google.com/citations?hl=vi&user=VoAaVRAAAAAJ',
            'https://scholar.google.com/citations?hl=vi&user=lsFfh2gAAAAJ',
            'https://scholar.google.com/citations?hl=vi&user=KrIDP2sAAAAJ',
            'https://scholar.google.com/citations?hl=vi&user=7eUhW3MAAAAJ',
            'https://scholar.google.com/citations?hl=vi&user=YVsTSNoAAAAJ',
            'https://scholar.google.com/citations?hl=vi&user=5q4fhUoAAAAJ',
            'https://scholar.google.com/citations?hl=vi&user=duBlF_YAAAAJ',
            'https://scholar.google.com/citations?hl=vi&user=8k8OgJIAAAAJ',
            'https://scholar.google.com/citations?hl=vi&user=l-Jd0tUAAAAJ',
            'https://scholar.google.com/citations?hl=vi&user=Iu8W_G0AAAAJ',
            'https://scholar.google.com/citations?hl=vi&user=2zk1CWkAAAAJ',
            'https://scholar.google.com/citations?hl=en&user=t4w1jE4AAAAJ',
            'https://scholar.google.com/citations?hl=en&user=7C7SiMEAAAAJ',
            'https://scholar.google.com/citations?hl=en&user=SQ6a30sAAAAJ',
            'https://scholar.google.com/citations?hl=en&user=-N-_kgsAAAAJ',
            'https://scholar.google.com/citations?hl=en&user=irm1Dd4AAAAJ'
        ]
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
        
        # Get user_id from URL
        user_id = response.url.split("user=")[1].split("&")[0]
        
        # Make request
        self.driver.get(response.url)

        # Get all rows in the table from webdriver response, each paper is in a row
        rows = response.xpath("//table[@id='gsc_rsb_st']//tbody//td[@class='gsc_rsb_std']")

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
        
        output_path = get_path([self.ROOT_DIR, "data", "sample_comparision", "hindex.csv"])
        with open(output_path, "a") as f:
            f.write("\n%s, %d, %d, %d, %d, %d, %d, %s, %s" % (user_id,citations_all,citations_s2014,\
                                                            hindex_all,hindex_s2014,i10index_all,i10index_s2014, \
                                                            coauthor_ids, coauthor_names))
            f.close()
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


