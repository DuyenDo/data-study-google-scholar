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

        # Configure webdriver
        if platform.system() == 'Windows':
            chromedriver_path = get_path([self.ROOT_DIR, "libs", "chromedriver.exe"])
        else:
            chromedriver_path = get_path([self.ROOT_DIR, "libs", "chromedriver"])
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=op)
        self.driver.implicitly_wait(60)

        # Get top universities from www.topuniversities.com
        ts = int(time.time())
        url = "https://www.topuniversities.com/sites/default/files/qs-rankings-data/914824.txt?_={}".format(ts)
        
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        data = json.loads(webpage.decode())
        data_df = pd.DataFrame.from_records(data['data'])
        data_df['rank_display'] = data_df['rank_display'].str.replace('=','')

        top = 100
        top_north_america = self.get_top_by_region(data_df, 'North America', top)
        top_europe = self.get_top_by_region(data_df, 'Europe', top)
        top_asia = self.get_top_by_region(data_df, 'Asia', top)
        self.top_uni = pd.concat([top_north_america, top_europe, top_asia], ignore_index=True)
        
        self.count = 0

    def start_requests(self):

        urls_top_uni = ('https://scholar.google.com/scholar?hl=en&q=' + self.top_uni['name_for_searching_gs'].astype(str))\
                        .to_list()

        for url in urls_top_uni:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Make request
        self.driver.get(response.url)

        try:
            org_id = response.xpath("//div[@class='gs_ob_inst_r']/a/@href").get().split('org=')[1].split('&')[0]
        except:
            org_id = 'Not found | {}'.format(response.url)
        time.sleep(10)
        
        name_for_searching_gs = response.url.split('&q=')[1].split('&')[0]
        top_uni = self.top_uni
        top_uni.loc[(top_uni.name_for_searching_gs == name_for_searching_gs),'org_id']=org_id
        self.top_uni = top_uni

        self.count += 1

        if self.count == self.top_uni.shape[0]:
            csv_path = get_path([self.ROOT_DIR, "data", "university", "top_university.csv"])
            self.top_uni.to_csv(csv_path, index=False)
        
    def get_top_by_region(self, df, region, top):
        sub_df = df.loc[df['region'] == region]
        sub_df['rank'] = sub_df['rank_display'].apply(lambda x: int(str(x).split('-')[0]))
        sub_df_top= sub_df.sort_values(by=['rank']).head(top)
        sub_df_top['name_for_searching_gs'] = sub_df_top['title'].apply(lambda x: re.sub(' ', '+', re.sub(r'\([^\)]+\)', '', x).strip()))
        sub_df_top['org_id'] = '-1'
        return sub_df_top