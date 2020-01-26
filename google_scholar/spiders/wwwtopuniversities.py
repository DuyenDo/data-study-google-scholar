import scrapy
from scrapy.http import TextResponse
from scrapy.selector import Selector

from selenium import webdriver

from urllib.request import Request, urlopen

import json

import pandas as pd

import os
import sys
import platform
import time
import re

from utils.tools import get_path, write_csv, write_pickle, monitor_crawler


class GSSpider(scrapy.Spider):
    name = "topuniversities"

    def __init__(self):
        self.ROOT_DIR = os.path.dirname(sys.modules['__main__'].__file__)

    def start_requests(self):

        df = pd.read_csv('top_asia.csv')
        urls_top_uni = ('https://scholar.google.com/scholar?hl=en&q=' + df['name_for_searching_gs'].astype(str))\
                        .to_list()[0:3]

        for url in urls_top_uni:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print("hello")
        # Configure webdriver
        if platform.system() == 'Windows':
            chromedriver_path = get_path([self.ROOT_DIR, "libs", "chromedriver.exe"])
        else:
            chromedriver_path = get_path([self.ROOT_DIR, "libs", "chromedriver"])
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=op)
        self.driver.implicitly_wait(60)
        # Make request
        self.driver.get(response.url)
        time.sleep(30)

        try:
            org_id = ''
            org_ids = response.xpath("//*[@class='gs_ob_inst_r']//a//@href").getall()
            for i in org_ids:
                org_id = org_id.join(i.split('org=')[1].split('&')[0].join(' | '))
        except Exception as e:
            print(e)
            org_id = 'Not found | {}'.format(response.url)
        
        name_for_searching_gs = response.url.split('&q=')[1].split('&')[0]

        with open('top_asia_id.csv', "a") as f:
            f.write("\n%s, %s" % (name_for_searching_gs,org_id))
            f.close()
        self.driver.close()

        
