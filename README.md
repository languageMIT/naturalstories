# Natural Stories Corpus

**Update 2020-11-11**: The repository has been updated with corrected alignments between SPR RTs and tokens in Story 3. In the previously-released files, the words after position 230 in Story 3 were mis-aligned with SPR RTs by one position. In the new files and alignment scripts, these errors have been corrected. For more details, see the `README` file in the `naturalstories_RT` directory. Thanks to Luca Campanelli and Cory Shain for helping us find and correct this issue.

This is a corpus of naturalistic stories meant to contain varied, low-frequency syntactic constructions.
There are a variety of annotations and psycholinguistic measures available for the stories.

The stories in with their various annotations are coordinated around the file `words.tsv`, which specifies a unique code for each token in the story under a variety of different tokenization schemes.
For example, the following lines in `words.tsv` cover the phrase `the long-bearded mill owners.`:

```
1.54.whole      the
1.54.word       the
1.54.1  the
1.55.whole      long - bearded
1.55.word       long - bearded
1.55.1  long
1.55.2  -
1.55.3  bearded
1.56.whole      mill
1.56.word       mill
1.56.1  mill
1.57.whole      owners .
1.57.word       owners
1.57.1  owners
1.57.2  .
```

The first column is the token code; the second is the token itself. For example, `1.57.whole` represents the token `owners.` and `1.57.word` represents the token `owners`.
The token code consists of three fields:

1. The id of the story the token is found in,
2. The number of the token in the story,
3. An additional field whose value is `whole` for the entire token including punctuation, `word` for the token stripped of punctuation to the left and right, and then 1 through n for each sub-token in `whole` as segmented by NLTK's TreebankWordTokenizer.

The various annotations (frequencies, parses, RTs, etc.) should reference these codes so that we can track tokens uniformly.

If you use the corpus please cite:
```
@article{futrell2021natural,
author={Richard Futrell and Edward Gibson and Harry J. Tily and Idan Blank and Anastasia Vishnevetsky and Steven T. Piantadosi and Evelina Fedorenko},
year={2021},
title={The Natural Stories corpus: A reading-time corpus of English texts containing rare syntactic constructions},
journal={Language Resources and Evaluation},
volume={55},
number={1},
pages={63--77}}
```

Deep syntactic annotations following a categorial grammar are also available [here](https://github.com/modelblocks/modelblocks-release) (see [paper](http://lrec-conf.org/workshops/lrec2018/W9/pdf/9_W9.pdf)).
