
# [Semester Project] The First Data Study of Google Scholar

## Member: 
**DO Thi Duyen - LE Ta Dang Khoa**

## Outline

### 1. Collect data from Google Scholar

- Packages:
> - _Scrapy_ for crawling: http://doc.scrapy.org/en/latest/
>
>    ```$pip install scrapy```
> - _Selenium_ and _Webdriver_ for JavaScript actions (e.g. click '_Show more_'): https://pypi.org/project/selenium/
>
>	```$pip install -U selenium```
>
>   Download webdriver (chromedriver.exe/geckodriver.exe/...) and put it in ```google_scholar/libs```
>	For linux server: ```$sudo apt-get install -y chromium-browser```

- Spiders: `google_scholar/spiders`
> -	Get list of papers given user URLs
		```google_scholar/spiders/papers_spider.py```
> - Get list of papers which cited the given paper
		```google_scholar/spiders/citations_spider.py```

- Run: ```$python3 google_scholar/runner.py```

### 2. Process and analyse