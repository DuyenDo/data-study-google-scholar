import os
from scrapy.cmdline import execute

os.chdir(os.path.dirname(os.path.realpath(__file__)))

# try:
#     execute(
#         [
#             'scrapy',
#             'crawl',
#             'papers',
#             '-a', 'input_file=authors_orgID_8539678734835078480.csv'
#         ]
#     )
# except SystemExit:
#     pass

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

# try:
#     execute(
#         [
#             'scrapy',
#             'crawl',
#             'citations',
#             '-a', 'input_dir=authors_orgID_7868974552293588111',
#             '-a', 'input_file=papers-of-authorID-_b6dDHMAAAAJ.csv'
#             # if arg 'input_file' is specified: read 'data/papers/<input_dir>/<input_file>.csv'
#             # else: read 'data/papers/input_dir/*.csv'
            
#         ]
#     )
# except SystemExit:
#     pass

try:
    execute(
        [
            'scrapy',
            'crawl',
            'data_comparison_gs'
        ]
    )
except SystemExit:
    pass