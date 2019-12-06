import os
import pickle

import scrapy
from scrapy.http import TextResponse

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class GSSpider(scrapy.Spider):
    name = "papers_summary"

    def start_requests(self):
        # Scholar-URL of the concern user
        url = "https://scholar.google.com/citations?user=" + self.id + "&hl=en"

        # Do the scraping
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Create a webdriver (Ubuntu, Chrome 78)
        # Use the driver to open the URL
        chromedriver_path = os.path.join(os.path.dirname(__file__),
                                         '../../libs/chromedriver')
        self.driver = webdriver.Chrome(chromedriver_path)
        self.driver.get(response.url)

        # Click 'Show more' until this button is disabled
        clicked_response = None
        while True:
            try:
                # Find button 'Show more'
                next = self.driver.find_element_by_xpath(
                    '//button[@id="gsc_bpf_more"][not(@disabled)]'
                )

                # Click the "Show More "button, wait for 3 seconds
                next.click()
                self.driver.implicitly_wait(3)
            except NoSuchElementException:
                # When button 'Show more' is disabled, get the text response
                clicked_response = TextResponse(url=response.url,
                                                body=self.driver.page_source,
                                                encoding='utf-8')
                # Close the webdriver
                self.driver.close()
                break

        # CREATE the papers_summary list
        papers_summary = []

        # Get all rows in the papers-table of the webpage
        # Each row represent a paper
        rows = clicked_response.xpath(
            "//table[@id='gsc_a_t']//tr[@class='gsc_a_tr']"
        )

        # For each paper, get:
        # + title,
        # + platform published
        # + citations count
        for row in rows:
            title = row.xpath(".//td[@class='gsc_a_t']/a/text()").get()

            platform = row.xpath(".//td[@class='gsc_a_t']/div[2]/text()").get()
            if platform is None:
                platform = ""

            citations = row.xpath(".//td[@class='gsc_a_c']/a/text()").get()
            citations_count = 0 if citations is None else int(citations)

            # Create a dictionary for each paper
            paper = {
                'Title': title,
                'Platform': platform,
                'Citations': citations_count
            }

            # Add to papers_summary
            papers_summary.append(paper)

        # SAVE the papers_summary list to a pickle file
        data_folder = os.path.join(os.path.dirname(__file__), '../../data/')

        filename = "{}{}.pkl".format(data_folder, self.id)
        with open(filename, "wb") as file:
            pickle.dump(papers_summary, file)
