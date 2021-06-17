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
    # Number of pages in corpus
    n_pages = len(corpus)
    # Number of links in page
    n_links = len(corpus[page])
    
    # If page has no links, assign equal probability of selecting all pages: 1/number of pages in corups
    if not n_links:
        prob_dist = dict.fromkeys(corpus.keys(), 1/n_pages)
    # Else, assign each page a probability: (1 - damping_factor)/number of pages in corpus
    else:
        # for pg in corpus:
        #     prob_dist[pg] = (1 - damping_factor)/n_pages
        prob_dist = dict.fromkeys(corpus.keys(), (1 - damping_factor)/n_pages)

        # If at least 1 outgoing link, assign probability for each link in 'page': damping_factor/number of links in page
        for link in corpus[page]: 
            prob_dist[link] += damping_factor/n_links
    
    return prob_dist

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Start with a page at random
    surf_page = random.choice(list(corpus))
    # pageranks dictionary for all known corpus pages
    pageranks = dict.fromkeys(corpus.keys(),0)

    # Repeat for n samples
    for i in range(n):
        # Count each page hit for n samples
        pageranks[surf_page] += 1
        # Generate a sample probability distribution from current page
        sample = transition_model(corpus, surf_page, damping_factor)
        # From current page, select new page at random but weighted according to probability distribution
        weighted_page = random.choices(list(sample), weights = sample.values(), k=1)
        # Assign list item as current page
        surf_page = weighted_page[0]

    # Calculate proportion of hits for each page (dictionary comprehension)
    pageranks = {page: hits/n for page, hits in pageranks.items()}

    return pageranks

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # All page names
    all_pages = corpus.keys()
    # Number of pages in corpus
    n_pages = len(corpus)
    # Assign each page an initial probability: 1/n_pages
    pageranks = dict.fromkeys(all_pages, 1/n_pages)
    # Track changed pagerank
    delta = dict.fromkeys(all_pages, 1)

    # Iterate until convergence, where all pagerank change < 0.001
    while any(d > 0.001 for d in delta.values()):
        # For each page
        for page in pageranks:
            prob = 0
            # Find parent pages to the page
            for parent_page in corpus:
                parent_links = corpus[parent_page]
                # If a parent page has no links, assume a link to every page
                if not parent_links:
                    parent_links = all_pages
                # Sum pagerank of all parent pages/links on parent pages    
                if page in parent_links:
                    prob += pageranks[parent_page]/len(parent_links)
            # Calculate new page rank
            new_pagerank = ((1 - damping_factor)/n_pages) + (damping_factor * prob)
            # Store the change in page rank
            delta[page] = abs(new_pagerank - pageranks[page])
            # Assign new pagerank to page
            pageranks[page] = new_pagerank

    return pageranks   

if __name__ == "__main__":
    main()
