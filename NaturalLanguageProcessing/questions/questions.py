import nltk
import sys
import os
import numpy as np

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])

    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)
    
    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    
    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
      
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    
    for match in matches:
        print(match)

def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    filesnames = dict()
    for filename in os.listdir(directory):
        with open('corpus/{}'.format(filename), 'r') as file:
            data = file.read().replace('\n','')
        filesnames[filename] = data

    return filesnames

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    document = document.replace('.',' . ')
    document = nltk.word_tokenize(document)
    document = [word.lower() for word in document if word.lower() not in 
                nltk.corpus.stopwords.words("english") and 
                (word.isalpha() or word.isnumeric())]
    return document

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # get all words in corpus
    # If dictionaries are passed to the update() method, 
    # the keys of the dictionaries are added to the set.
    words = set()
    for filename in documents:
        words.update(documents[filename])
    idfs = dict()
    for word in words:
        f = 0
        for filename in documents:
            if word in documents[filename]:
                f += 1
        if f != 0:
            idfs[word] = np.log(len(documents)/f)        
    return idfs

def tf_idf(filename,idfs,word):
    #calculating term frequency
    tf = filename.count(word)
    return idfs[word]*tf

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    n_words = dict()
    for filename in files:
        n_words[filename] = 0
        for word in query:
            n_words[filename] += tf_idf(files[filename],idfs,word)
    n_words =  dict(sorted(n_words.items(), key=lambda item: item[1], reverse= True))
    return ([k for k,v in n_words.items()][:n])

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    n_sentences = dict()
    for sentence,words in sentences.items():
        
        possible_word = query.intersection(words) 
        n_sentences[sentence]=0
        
        idf = 0
        for word in possible_word:
            idf += idfs[word]

        query_term_density = len(possible_word)/len(words)
        n_sentences[sentence] = {'idf': idf, 'qtd':query_term_density}

    n_sentences = dict(sorted(n_sentences.items(),key=lambda item: (item[1]["idf"],item[1]["qtd"]), reverse = True))
    arr = [k for k,v in n_sentences.items()]
    return arr[:n]   

if __name__ == "__main__":
    main()
