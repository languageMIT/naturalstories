from __future__ import print_function
import sys
from collections import namedtuple
import itertools
import re


WORD_RE = re.compile("(?<!-NONE-) ([^ \)]+)\)")
CONLLX_WORD = 1
CONLLX_MISC = -1

Word = namedtuple('Word', 'story_id word_id content'.split())
WordPart = namedtuple('WordPart', 'story_id word_id part_id content'.split())

append = itertools.chain

def get_parts(word, parts):
    if isinstance(word, Word):
        return parts[word.story_id, word.word_id]
    else:
        return [word]

def align_penn(words, parts, lines):
    words = iter(words)
    for line in lines:
        found = find_words(line)
        offset = 0
        for i_word_start, i_word_end, word_found in found:
            curr_word = next(words)
            curr_parts = get_parts(curr_word, parts)
            if words_aligned(word_found, curr_word):
                if len(curr_parts) > 1: # hyphenated words
                    curr_word = WordPart(curr_word.story_id,
                                         curr_word.word_id,
                                         'word',
                                         curr_word.content)
                line, inc_offset = add_code(line,
                                            curr_word,
                                            i_word_start + offset,
                                            i_word_end + offset)
                offset += inc_offset
            else: # otherwise look at the parts of the word
                assert isinstance(curr_word, Word)
                if any(part.content == '-' for part in curr_parts):
                    # handle special case of "x-y,+"
                    # where "x-y" corresponds to id.id.word,
                    # and ",+" is id.id.4 onward
                    i_first_punct = first(i for i, part in enumerate(curr_parts)
                                            if not (part.content.isalpha()
                                                    or part.content == '-'))
                    word_parts = curr_parts[:i_first_punct] 
                    curr_part = WordPart(
                        curr_word.story_id,
                        curr_word.word_id,
                        'word',
                        " ".join(part.content for part in word_parts)
                    )
                    words = append(curr_parts[i_first_punct:], words)
                else:
                    curr_part = curr_parts[0]
                    assert words_aligned(word_found, curr_part)
                    assert len(curr_parts) > 1, (line, curr_parts)
                    words = append(curr_parts[1:], words)
                line, inc_offset = add_code(line,
                                            curr_part,
                                            i_word_start + offset,
                                            i_word_end + offset)
                offset += inc_offset
        yield line

def penn_words(lines):
    for line in lines:
        for i_start, i_end, word in find_words(line):
            content, code = word.split("/")
            yield (i_start, i_end), content, code

def itersplit(fn, xs):
    chunk = []
    for x in xs:
        if fn(x):
            if chunk:
                yield chunk
            chunk = []
        else:
            chunk.append(x)
    yield chunk

def penn_sentences(lines):
    return itersplit(lambda line: line.startswith("(ROOT"), lines)

def stanford_sentences(lines):
    return itersplit(lambda line: not line.strip(), lines)

conllx_sentences = stanford_sentences

def align_ud(aligned_penn, lines):
    for penn_sentence, ud_sentence in zip(penn_sentences(aligned_penn),
                                          conllx_sentences(lines)):
        the_penn_words = list(penn_words(penn_sentence))
        # Make a dict of indices to (word, code) pairs
        penn_word_ids = dict(
            enumerate(((word, code) for _, word, code in the_penn_words))
        )
        for i, line in enumerate(ud_sentence):
            parts = line.split("\t")
            word = parts[CONLLX_WORD]
            assert word == the_penn_words[i][1]
            parts[CONLLX_MISC] = "TokenId=%s" % penn_word_ids[i][-1]
            yield "\t".join(parts) + "\n"
        yield "\n"

def align_stanford(aligned_penn, lines):
    for penn_sentence, stanford_sentence in zip(penn_sentences(aligned_penn),
                                                 stanford_sentences(lines)):
        # Make a dict of indices to (word, code) pairs
        penn_word_ids = dict(enumerate(((word, code)
                                        for _, word, code in penn_words(penn_sentence)),
                                        1))
        penn_word_ids[0] = 'ROOT', '0'
        for line in renumber_stanford_sentence(stanford_sentence, penn_word_ids):
            yield line
        yield "\n"

STANFORD_WORD_1_RE = re.compile("\(([^\d]+)-(\d+), ")
STANFORD_WORD_2_RE = re.compile(", ([^\d]+)-(\d+)\)")
def stanford_words(line):
    first_word_matches = list(STANFORD_WORD_1_RE.finditer(line))
    assert len(first_word_matches) == 1
    first_word = first_word_matches[0]
    first_word_content = first_word.groups()[0]
    first_word_start = first_word.start()
    first_word_id = int(first_word.groups()[1])

    second_word_matches = list(STANFORD_WORD_2_RE.finditer(line))
    assert len(second_word_matches) == 1
    second_word = second_word_matches[0]
    second_word_content = second_word.groups()[0]
    second_word_start = second_word.start()
    second_word_id = int(second_word.groups()[1])

    return ((first_word_start, first_word_content, first_word_id),
            (second_word_start, second_word_content, second_word_id))

def renumber_stanford_sentence(stanford_lines, word_ids):
    for line in stanford_lines:
        (i_w1, w1, w1_id), (i_w2, w2, w2_id) = stanford_words(line)
        assert w1 == word_ids[w1_id][0]
        assert w2 == word_ids[w2_id][0]
        parts = [
            line[:(i_w1 + 1)],
            w1,
            "-",
            word_ids[w1_id][1],
            ", ",
            w2,
            "-",
            word_ids[w2_id][1],
            ")",
            "\n"
        ]
        yield "".join(parts)
        
def first(xs):
    return next(iter(xs))

def words_aligned(string, word):
    return (string == normalize(word.content)
            or string == "``" and word.content == "'"
            or string == "''" and word.content == "'"
            or string == "-LRB-" and word.content == "("
            or string == "-RRB-" and word.content == ")"
            )

def normalize(string):
    return string.replace(" ", "")

def add_code(line, word, i_start, i_end):
    code = ".".join(map(str, word[:-1]))
    return "%s/%s%s" % (line[:i_end], code, line[i_end:]), len(code) + 1

def read_words(lines):
    words = []
    parts = {}
    for line in lines:
        code, content = line.strip().split("\t")
        story_id, word_id, part_id = code.split(".")
        if part_id == 'whole':
            words.append(Word(story_id, word_id, content))
        else:
            try:
                part_id = int(part_id)
                part = WordPart(story_id, word_id, part_id, content)
                if (story_id, word_id) in parts:
                    parts[story_id, word_id].append(part)
                else:
                    parts[story_id, word_id] = [part]
            except ValueError:
                pass
    return words, parts

def printerr(string):
    print(string, file=sys.stderr)

def find_words(line):
    matches = WORD_RE.finditer(line)
    for match in matches:
        yield match.start() + 1, match.end() - 1, match.groups()[0]

def main(words_filename, penn_filename, ud_filename=None):
    with open(words_filename, 'rt') as infile:
        words, parts = read_words(infile)
    with open(penn_filename, 'rt') as infile:
        aligned_penn_lines = list(align_penn(words, parts, infile))
    if ud_filename is None:
        for line in aligned_penn_lines:
            print(line, end="")
    else:
        with open(ud_filename, 'rt') as infile:
            for line in align_ud(aligned_penn_lines, infile):
                print(line, end="")

if __name__ == '__main__':
    main(*sys.argv[1:])
    
