import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    n_pages = len(corpus)
    probability_distribution = {}

    links = corpus[page]

    if links:
        for p in corpus:
            probability_distribution[p] = (1 - damping_factor) / n_pages
        for link in links:
            probability_distribution[link] += damping_factor / len(links)
    else: 
        for p in corpus:
            probability_distribution[p] = 1 / n_pages

    return probability_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    pagerank = {page: 0 for page in corpus}
    pages = list(corpus.keys())

    current_page = random.choice(pages)
    pagerank[current_page] += 1

    for _ in range(1, n):
        distribution = transition_model(corpus, current_page, damping_factor)
        current_page = random.choices(
            population=list(distribution.keys()),
            weights=list(distribution.values()),
            k=1
        )[0]
        pagerank[current_page] += 1

    for page in pagerank:
        pagerank[page] /= n

    return pagerank


def iterate_pagerank(corpus, damping_factor, tolerance=0.001):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    n = len(corpus)
    pagerank = {page: 1 / n for page in corpus}

    no_links = {page for page in corpus if len(corpus[page]) == 0}
    for page in no_links:
        corpus[page] = set(corpus.keys())

    while True:
        new_pagerank = {}
        for page in corpus:
            total = 0
            for possible_page in corpus:
                if page in corpus[possible_page]:
                    total += pagerank[possible_page] / len(corpus[possible_page])
            new_pagerank[page] = (1 - damping_factor) / n + damping_factor * total

        if all(abs(new_pagerank[p] - pagerank[p]) < tolerance for p in pagerank):
            break
        pagerank = new_pagerank.copy()

    return pagerank


if __name__ == "__main__":
    main()
