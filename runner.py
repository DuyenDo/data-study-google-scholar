import sys
import pickle

from scrapy.cmdline import execute
from utils import filter_bad_papers, compute_h_index

try:
    # READ a TEXT FILE for ID and WORDS
    with open(sys.argv[1], 'r') as req_file:
        ID, words = req_file.readlines()[:2]

    user_id = ID.rstrip()
    keywords = words.rstrip().split(",")

    # EXECUTE SCRAPPING
    execute(
        "scrapy crawl papers_summary -a id={}".format(user_id).split()
    )
except SystemExit:
    # SCRAPPING FINISHED:
    # 1. Read the corresponding data-file
    with open("data/{}.pkl".format(user_id), "rb") as data_file:
        papers_summary = pickle.load(data_file)

    # 2. Filter bad papers
    adjusted_citations_counts = filter_bad_papers(
        keywords, papers_summary
    )

    # 3. Re-compute H-Index
    print("===================")
    print("ID: {}".format(user_id))
    print("Keywords: {}".format(keywords))
    print("ADJUSTED CITATIONS: {}".format(sum(adjusted_citations_counts)))
    print("ADJUSTED H-INDEX: {}".format(
        compute_h_index(adjusted_citations_counts)
    ))
