import os
from scrapy.cmdline import execute

os.chdir(os.path.dirname(os.path.realpath(__file__)))

try:
    execute(
        [
            'scrapy',
            'crawl',
            'papers_2',
            '-a', 'input_file=authors_eurecom_fr.csv'
        ]
    )
except SystemExit:
    pass