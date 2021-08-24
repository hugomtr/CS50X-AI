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
    print(corpus)

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
    #Initialize a hash of zero
    transition = dict((page,0) for page in corpus)
    
    #update probability for the link page     
    pages_links = corpus[page]
    if pages_links:
        for link_page in pages_links:
            transition[link_page] += 0.85/(len(pages_links))
        for curr_page in corpus:
            transition[curr_page] += 0.15/(len(corpus))
    #if there is no pages_links
    else:
        for curr_page in corpus:
            transition[curr_page] += 1/(len(corpus))
    return transition


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    first_sample = random.choice(list(corpus.keys()))
    
    #keeping track of all the sample
    samples = [first_sample]
    
    #keeping track of the previous sample
    previous_sample = first_sample
    for i in range(n):
        current_sample = random.choices(list(corpus.keys()),weights=list(transition_model(corpus,previous_sample,DAMPING).values())).pop()
        samples.append(current_sample)
        previous_sample = current_sample
    
    sample_proportion = dict((page,0) for page in corpus)

    #calculate the proportion
    for sample in samples:
        for page in corpus:
            if sample == page:
                sample_proportion[page] += 1
    
    for page in sample_proportion:
        sample_proportion[page] /= n

    return sample_proportion


def get_links_page(corpus):
    all_links = dict((page,set()) for page in corpus)
    for page in corpus:
        for link in corpus[page]:
            if link in corpus[page]:
                all_links[link].add(page)
    return all_links


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    d = DAMPING
    current_page_rank = dict((page,1/N) for page in corpus)
    previous_page_rank = dict((page,1/N) for page in corpus)
    condition = False
    while not condition:
        for page in corpus:
            sm = 0
            if corpus[page]:
                all_links = get_links_page(corpus)
                for link in all_links[page]:
                    sm += previous_page_rank[link]/(len(corpus[link]))
            current_page_rank[page] = (1-d)/N +d*sm

        for page in corpus: 
            if abs(previous_page_rank[page]-current_page_rank[page])>0.0009:
                condition = False
            else:
                condition = True 

        for page in corpus:
            previous_page_rank[page] = current_page_rank[page]

    return current_page_rank




if __name__ == "__main__":
    main()
