import nltk
nltk.download('stopwords')
import sys
import os
import string
import math

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
    corpus_dict = dict()
    # For all files in the directory
    for filename in os.listdir(directory):
        # Open filepath
        with open(os.path.join(".", directory,filename), 'r') as f:
        # save txt against filename
            corpus_dict[filename] = f.read()
        # close file
        f.close()
    
    return corpus_dict


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    tokenized = nltk.word_tokenize(document.lower())
    stop_words = set(nltk.corpus.stopwords.words('english'))
    words = [word for word in tokenized if word not in string.punctuation and word not in stop_words]
    
    return words

def calc_idf(documents, word):
    """
    Helper function to calculate the idf for a given word
    Inputs:
        documents: dictionary, {document: list of words}
        word: string
    Outputs:
        idf: float, idf value of word
    """
    # Document count
    doc_count = len(documents)

    # Calculate document frequency of word
    df = 0
    for document in documents:
        if word in documents[document]:
            df += 1

    # Calcuate idf
    idf = math.log(doc_count/df)

    return idf

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # Document count
    doc_count = len(documents)

    idfs = dict()
    for document in documents:
        for word in documents[document]:
            if word not in idfs:
                idfs[word] = calc_idf(documents, word)

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    doc_vals = dict()

    # For each file
    for file in files:
        # list of words in the file
        words = files[file]
        # Intersect of words in both query and sentence
        intersect = set(words).intersection(query)
        # Initialise tf-idf for file = 0
        tf_idf = 0
        # For each query term in intersect (i.e. also in the file)
        for term in intersect:
            # Count the occurences of query term in the file
            t_count = words.count(term)
            # Calculate the query term frequency: tf(t,d) = count of t in d / number of words in d
            tf = t_count/len(words)
            # Sum tf-idf across all query terms
            tf_idf += tf*idfs[term]
        # Store tf-idf for file
        doc_vals[file] = tf_idf
    
    # Sort dictionary from high to low
    sorted_dict = dict(sorted(doc_vals.items(), key=lambda item: item[1], reverse = True))
    # List of dict keys from high to low
    sorted_files = list(sorted_dict.keys())

    return sorted_files[0:n]            

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_vals = dict()

    # For each sentence
    for sentence in sentences:
        # Set of words in the sentence
        words = set(sentences[sentence])
        # Intersect of words in both query and sentence
        matching_words = words.intersection(query)
        # Initialise matching word measure for sentence = 0
        mwm = 0
        # For each word in the intersect
        for word in matching_words:
            # Sum idf across all terms
            mwm += idfs[word]
        # Calculate query term density
        qtd = len(matching_words)/len(words)
        # Store sentence scores
        sentence_vals[sentence] = {'mvm': mwm, 'qtd': qtd}
    # Sort dictionary high to low, first by mwm and in the instance of a tie, by qtd
    sorted_dict = dict(sorted(sentence_vals.items(), key=lambda item: (item[1]['mvm'], item[1]['qtd']), reverse = True))
    # Sorted keys, high to low
    sorted_sentences = list(sorted_dict.keys())

    return sorted_sentences[0:n] 


if __name__ == "__main__":
    main()
