import re


def filter_bad_papers(keywords, papers_summary):
    for idx, paper in enumerate(papers_summary):
        title = paper['Title']
        platform = paper['Platform']

        for kw in keywords:
            if (re.search(kw, title, re.IGNORECASE) or
                    re.search(kw, platform, re.IGNORECASE)):
                print("BAD PAPER: {}; AT {}".format(title, platform))

                papers_summary[idx] = None
                break

    return [summary['Citations'] for summary in papers_summary
            if summary is not None]


def compute_h_index(citations_counts):
    citations_counts.sort(reverse=True)

    h_index = 0
    for idx, count in enumerate(citations_counts):
        if count < (idx + 1):
            h_index = idx
            break

    return h_index
