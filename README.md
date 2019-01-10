# Natural Stories Corpus

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
@inproceedings{futrell2018natural,
author={Richard Futrell and Edward Gibson and Harry J. Tily and Idan Blank and Anastasia Vishnevetsky and Steven T. Piantadosi and Evelina Fedorenko},
title={The Natural Stories Corpus},
year={2018},
booktitle={Proceedings of LREC 2018, Eleventh International Conference on Language Resources and Evaluation},
pages={76--82},
address={Miyazaki, Japan}}
```

Deep syntactic annotations following a categorial grammar are also available [here](https://github.com/modelblocks/modelblocks-release) (see [paper](http://lrec-conf.org/workshops/lrec2018/W9/pdf/9_W9.pdf)).
