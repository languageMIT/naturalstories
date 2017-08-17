#!/usr/bin/python2
""" get frequency information for tokens in stories from Google Books """
from __future__ import print_function
import sys
import copy
import itertools as it
from collections import deque, namedtuple
import subprocess
import re

import nltk
import zs

#NGRAMS_LOCATION = "http://bolete.ucsd.edu/njsmith/google-books-eng-us-all-20120701-%dgram.zs"
NGRAMS_LOCATION = "http://cpl-data.ucsd.edu/zs/google-books-20120701/eng-all/google-books-eng-all-20120701-%dgram.zs"
ZS_CMD = "zs dump --prefix=\"%s\\t\" %s"
MAX_AVAILABLE_ORDER = 5
CUTOFF_YEAR = 1990
VERBOSE = 1

tokenizer = nltk.tokenize.treebank.TreebankWordTokenizer()

StoryWord = namedtuple('StoryWord', 'story_id word_id word'.split())
Token = namedtuple('Token', 'part_id content'.split())
StoryToken = namedtuple('StoryToken','story_id word_id part_id content'.split())

def sliding(iterable, n):
    """ Sliding

    Yield adjacent elements from an iterable in a sliding window
    of size n.

    Parameters:
        iterable: Any iterable.
        n: Window size, an integer.

    Yields:
        Tuples of size n.

    Example:
        >>> lst = ['a', 'b', 'c', 'd', 'e']
        >>> list(sliding(lst, 2))
        [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e')]

    """
    xss = it.tee(iterable, n)
    for i, xs in enumerate(xss):
        for _ in xrange(i):
            next(xs)
    return it.izip(*xss)

def memoize(f):
    """ Memoize a single-argument function. """
    class Memodict(dict):
        def __missing__(self, key):
            result = self[key] = f(key)
            return result
    memodict = Memodict()
    wrapper = memodict.__getitem__
    return wrapper

@memoize
def tokenize_word(word):
    def gen():
        broken_word = break_word(word)
        yield Token('whole', broken_word)
        yield Token('word', get_lexical_word(broken_word))
        for i, content in enumerate(broken_word, 1):
            yield Token(i, [content])
    return list(gen())

initial_apostrophe_re = re.compile(" '([^ ])")
TITLES = set("Mr Mrs Ms Dr".split())
def break_word(string):
    string = " %s " % string
    string = string.replace("-", " - ")
    string = initial_apostrophe_re.sub(r" ' \1", string)
    string = string.replace(" ' s ", " 's ")
    parts = tokenizer.tokenize(string)
    if len(parts) >= 2 and parts[-1] == "." and parts[-2] in TITLES:
        del parts[-1]
        parts[-1] += "."
    return parts

def read_tok_file(filename):
    """ Read a .tok file, returning an iterator yielding 2-tuples:
    ((story_id (int), word_id (int)), word (string))
    """
    with open(filename, 'rb') as infile:
        next(infile) # skip header
        yield StoryWord(0, 0, ".") # yield a sentence boundary word first
        for line in infile:
            word, word_id, story_id = line.strip().split("\t")
            yield StoryWord(int(story_id), int(word_id), word)

def get_lexical_word(word_parts):
    """ Strip away punctuation surrounding a word. Preserve 's. """
    def gen():
        for part in word_parts:
            if (part.isalpha()
                or part == "-"
                or (any(x.isalpha() for x in part) and "'" in part)):
                yield part
    return list(gen())

def generate_tokens_in_context(story_word_ngrams):
    """ An ngram query is a (StoryToken, list of words) pair """
    for story_word_ngram in story_word_ngrams:
        last_story_word = story_word_ngram[-1]
        story_id, word_id, _ = last_story_word
        context_words = [story_word.word for story_word in story_word_ngram[:-1]]
        tokens = tokenize_word(last_story_word.word)
        all_context = process_context(context_words)
        for token, context in contexts_for_tokens(tokens, all_context):
            story_token = StoryToken(story_id, word_id, token.part_id, token.content)
            yield story_token, context

def truncate_at_sentence_boundary(tokens, i):
    tokens = tokens[(i+1):]
    tokens.insert(0, "_START_")
    return tokens

def flatmap(f, xs):
    for x in xs:
        for y in f(x):
            yield y

def contexts_for_tokens(tokens, all_context):
    context = all_context[:]
    numbered_tokens = [t for t in tokens if isinstance(t.part_id, int)]
    numbered_tokens.sort() # story_id and word_id are the same so sorting means
                           # sorting by the next thing, which is part_id
    assert all(len(t.content) == 1 for t in numbered_tokens)
    for token in tokens:
        if token in numbered_tokens:
            tokens_to_add = numbered_tokens[:(token.part_id - 1)]
            words_to_add = [t.content[0] for t in tokens_to_add]
            yield token, context + words_to_add
        else:
            yield token, context

SENTENCE_BOUNDARY_PUNCTUATION = set(".?!")            
def process_context(context):
    context_parts = list(flatmap(break_word, context))
    result = context_parts
    for i, part in enumerate(context_parts):
        if part in SENTENCE_BOUNDARY_PUNCTUATION:
            if len(context_parts) > i + 1 and context_parts[i + 1] == "'":
                result = truncate_at_sentence_boundary(context_parts,i+1)
            else:
                result = truncate_at_sentence_boundary(context_parts, i)
    return result

def run_start_sentence_query():
    """ get frequency of the start sentence symbol """
    return 26652383826 # takes forever, so just hardwire the answer in
    #return get_freq(("_START_ ", 2))

def make_queries(story_tokens_in_context, ngram_order):
    for story_token, context in story_tokens_in_context:
        context = list(deque(context, maxlen=ngram_order - 1))
        word = story_token.content
        word_len = len(word)
        full_query = list(deque(context + word, maxlen=MAX_AVAILABLE_ORDER))
        if len(full_query) < ngram_order:
            continue
        new_context = full_query[:-word_len]
        if len(new_context) < ngram_order - 1:
            continue
        assert len(new_context) == ngram_order - 1
        yield story_token, full_query, new_context
        
def ngram_frequencies(story_words, ngram_order):
    story_word_ngrams = sliding(story_words, ngram_order)
    story_tokens_in_context = generate_tokens_in_context(story_word_ngrams)
    queries = make_queries(story_tokens_in_context, ngram_order)
    # Do this with imap so it is easy to swap in a parallel map
    # (A generator would be more natural otherwise.)
    def f((story_token, full_query, context)):
        if VERBOSE:
            print("running full query of order %d: %s" % (len(full_query),
                                                          full_query),
                  file=sys.stderr)
        full_freq = run_query(full_query)

        if not context:
            context_freq = 'NA'
        else:
            if context == ["_START_"]:
                if VERBOSE:
                    print("running start-of-sentence context query",
                          file=sys.stderr)
                context_freq = run_start_sentence_query()
            else:
                if VERBOSE:
                    print("running context query of order %d: %s"%(len(context),
                                                                    context),
                        file=sys.stderr)
                context_freq = run_query(context)
                
        if context_freq < full_freq:
            print("Warning! Context freq (%d) < full freq (%d) for line: %s"
                  % (context_freq, full_freq, context+word), file=sys.stderr)
        return story_token, full_freq, context_freq
    return it.imap(f, queries)

def escape(string):
    return string.replace('"', '\"')

def run_query(query):
    order = len(query)
    query = escape(" ".join(query)) 
    return get_freq((query, order))

@memoize
def get_freq((query, order)):
    lines = ZS[order].search(prefix=query + "\t")
    if VERBOSE > 1:
        lines = list(lines)
        print("\n".join(lines), file=sys.stderr)
    lines = (line.split("\t") for line in lines if line)
    return sum(int(freq) for words, year, freq, freq_b in lines
               if int(year) >= CUTOFF_YEAR)

def init_ZS():
    global ZS
    ZS = {}
    for i in xrange(1, MAX_AVAILABLE_ORDER + 1):
        if VERBOSE:
            print("Opening %s" % (NGRAMS_LOCATION % i), file=sys.stderr)
        ZS[i] = zs.ZS(url=NGRAMS_LOCATION % i)
                        
def close_ZS():
    for zs in ZS.itervalues():
        if zs is not None:
            zs.close()

def make_line(story_token, w_freq, c_freq, ngram_order):
    def gen():
        yield ".".join(map(str, [story_token.story_id,
                                 story_token.word_id,
                                 story_token.part_id,
                                ]))
        yield ngram_order
        yield " ".join(story_token.content)
        yield w_freq
        yield c_freq
    return "\t".join(map(str, gen()))

def main(filename, ngram_order):
    ngram_order = int(ngram_order)
    init_ZS()
    story_words = read_tok_file(filename)
    try:
        for story_token, w_freq, c_freq in ngram_frequencies(story_words,
                                                             ngram_order):
            if story_token.story_id != 0:
                print(make_line(story_token, w_freq, c_freq, ngram_order))
    finally:
        close_ZS()
    

if __name__ == '__main__':
    main(*sys.argv[1:])
    
