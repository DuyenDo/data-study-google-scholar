import scrapy
from scrapy.http import TextResponse
from selenium import webdriver
import os
import csv

class GSSpider(scrapy.Spider):
    name = "citations"

    def start_requests(self):
        # Citations of a paper
        urls = [
            'https://scholar.google.fr/scholar?oi=bibs&hl=en&cites=12738890041914893444'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        # Path to chromedriver.exe
        chromedriver_path = os.path.join(os.path.dirname(__file__), '..\\..\\libs\\chromedriver.exe')
        # Create a webdriver
        self.driver = webdriver.Chrome(chromedriver_path)
        
        # Get citationsId from citation URL
        citation_id = response.url.split("cites=")[1].replace(",", "_")

        # Create a list of papers which cited the orginal paper
        cited_by_list = []

        # Use webdriver to make request to a user's URL
        self.driver.get(response.url)

        # Create a variable for response from webdriver
        page_response = TextResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')

        self.parse_one_page(page_response, cited_by_list)

        # Click 'Show more' until this button is disabled to show full list of papers
        while True:
            try:
                # Find button 'Next' when it is not hidden
                self.driver.find_element_by_xpath("//div[@id='gs_n']//td[@align='left']/a").click()

                # Wait 3 seconds for loading page before next click
                self.driver.implicitly_wait(10)

                # Create a variable for response from webdriver
                next_page_response = TextResponse(url=self.driver.current_url, body=self.driver.page_source, encoding='utf-8')

                self.parse_one_page(next_page_response, cited_by_list)

            except Exception as e: 
                print(e)

                # Close webdriver
                self.driver.close()
                break

        data_folder = os.path.join(os.path.dirname(__file__), '..\\..\\data\\')
        # Create a filename
        file_cited_papers = '%scited-papers-%s.csv' % (data_folder, citation_id)
        # Write list of papers to csv file
        keys = cited_by_list[0].keys()
        with open(file_cited_papers, 'w', encoding='utf-8', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(cited_by_list)

    
    def parse_one_page(self, page_response, cited_by_list):

        rows = page_response.xpath("//div[@id='gs_res_ccl_mid']//div[@class='gs_ri']")

        # In each citation, get title of the paper, id of authors, name of authors
        # To avoid column errors when reading files, replace ',' in strings to ';'. The columns will be seperated by ','
        for row in rows:
            title_list = row.xpath(".//h3[@class='gs_rt']//text()").getall()
            title_str = ",".join(title_list).strip(' \t\n\r').replace(',', ';')
            author_ids_list = row.xpath(".//div[@class='gs_a']/a/@href").getall()
            author_ids_str = ",".join([author_id.split("user=")[1].split("&")[0] for author_id in author_ids_list])\
                                .strip(' \t\n\r').replace(',', ';')
            author_name_list = row.xpath(".//div[@class='gs_a']/a/text()").getall()
            author_name_str = ",".join(author_name_list).strip(' \t\n\r').replace(',', ';')
            cited_url = row.xpath(".//div[@class='gs_fl']/a[contains(text(),'Cited by')]/@href").get()

            # Create a dictionary for each paper
            cited_by = {
                'Title': title_str,
                'AuthorIDs': author_ids_str,
                'AuthorNames': author_name_str,
                'Cited_url': cited_url
            }

            cited_by_list.append(cited_by)