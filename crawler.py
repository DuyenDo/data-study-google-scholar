import os
from scrapy.cmdline import execute

os.chdir(os.path.dirname(os.path.realpath(__file__)))

try:
    execute(
        [
            'scrapy',
            'crawl',
            'papers',
            '-a', 'input_file=authors_orgID_8539678734835078480.csv'
        ]
    )
except SystemExit:
    pass

# try:
#     execute(
#         [
#             'scrapy',
#             'crawl',
#             'authors'
#         ]
#     )
# except SystemExit:
#     pass