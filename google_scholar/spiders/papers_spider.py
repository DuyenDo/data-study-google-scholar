import scrapy
from scrapy.http import TextResponse
from selenium import webdriver
import os
import csv

class GSSpider(scrapy.Spider):
    name = "papers"

    def start_requests(self):
        # URLs of users
        urls = [
            'https://scholar.google.fr/citations?user=WVLr6NYAAAAJ&hl=en',
            'https://scholar.google.fr/citations?user=GM-hJhQAAAAJ&hl=en'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        # Path to chromedriver.exe
        chromedriver_path = os.path.join(os.path.dirname(__file__), '..\\..\\libs\\chromedriver.exe')
        # Create a webdriver
        self.driver = webdriver.Chrome(chromedriver_path)
        
        # Get userId from user's URL
        user = response.url.split("user=")[1].split("&")[0]
        
        # Use webdriver to make request to a user's URL
        self.driver.get(response.url)

        # Create a variable for response from webdriver
        clicked_response = None

        # Click 'Show more' until this button is disabled to show full list of papers
        while True:
            try:
                # Find button 'Show more' when it is not disabled
                next = self.driver.find_element_by_xpath('//button[@id="gsc_bpf_more"][not(@disabled)]')
                # Click button
                next.click()
                # Wait 3 seconds for loading page before next click
                self.driver.implicitly_wait(3)
            except:
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

            # Create a dictionary for each paper
            paper = {
                'Title': title,
                'Authors': authors,
                'Conference': conference,
                'Cited_urls': cited_url,
                'Cited_count': cited_count,
                'Year': year
            }

            papers.append(paper)

        # Create a filename
        file_user_papers = 'papers-of-user-%s.csv' % user
        # Write list of papers to csv file
        keys = papers[0].keys()
        with open(file_user_papers, 'w', encoding='utf-8', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(papers)
    