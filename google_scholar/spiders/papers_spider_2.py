import scrapy
from scrapy.http import TextResponse
from selenium import webdriver
import os
import csv
import time
import pickle
import pandas as pd

class GSSpider(scrapy.Spider):
    name = "papers"

    def start_requests(self):

        path = os.path.join(os.path.dirname(__file__), '..\\..\\data\\')
        dataframe = pd.read_csv("%sauthors_list-standford.csv" % path)
        dataframe['AuthorID'] = 'https://scholar.google.com/citations?hl=en&user=' + dataframe['AuthorID'].astype(str)
        urls = dataframe['AuthorID'].to_list()[169:500]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        chromedriver_path = os.path.join(os.path.dirname(__file__), '..\\..\\libs\\chromedriver.exe')
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=op)
        self.driver.implicitly_wait(60)
        
        # Get userId from user's URL
        user = response.url.split("user=")[1].split("&")[0]
        
        # Use webdriver to make request to a user's URL
        self.driver.get(response.url)

        # Create a variable for response from webdriver
        clicked_response = None

        # Click 'Show more' until this button is disabled to show full list of papers
        while True:
            try:
                # Wait 15 seconds for loading page before next click
                time.sleep(15)
                # Find button 'Show more' when it is not disabled
                self.driver.find_element_by_xpath('//button[@id="gsc_bpf_more"][not(@disabled)]').click()
            except Exception  as e:
                print(e)
                # When button 'Show more' is disabled, get response from webdriver
                clicked_response = TextResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')
                # Close webdriver
                self.driver.close()
                break

        # Create a list of papers for the given user
        papers = []

        # Get all rows in the table from webdriver response, each paper is in a row
        rows = clicked_response.xpath("//table[@id='gsc_a_t']//tr[@class='gsc_a_tr']")

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

        data_folder = os.path.join(os.path.dirname(__file__), '..\\..\\data\\papers_standford\\')
        file_user_papers = '%spapers-of-authorID-%s.csv' % (data_folder, user)

        # Write to csv file
        keys = papers[0].keys()
        with open(file_user_papers, 'w', encoding='utf-8', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(papers)

        # Write to pickle
        filename = "{}papers-of-authorID-{}.pkl".format(data_folder, user)
        with open(filename, "wb") as pfile:
            pickle.dump(paper, pfile)
    