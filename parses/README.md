## Natural Stories Parses

### Penn Treebank Style
The directory `penn/` contains parses with some further corrections; these are the most up-to-date parses. The file `penn/all-parses.txt.penn` just contains the parses. The file `penn/all-parses-aligned.txt.penn` contains the parses with each word tagged with its code as defined in `words.tsv`.

`penn/` also contains a file `penn/all-parses-aligned-txt.penn.consfeatures`, which contains two columns: the first is a word code, the second is the number of constituents ended by that word.

### Universal Dependencies
The Penn Treebank style parses were automatically converted to Universal Dependencies CoNLL-X format, in `ud/stories.conllx`. In that file the final column is used to give the token ids.

### Stanford Dependencies
The directory `stanford/` contains the parses automatically converted into Stanford dependencies.
The file `stanford/all-parses.txt.stanford` contains the raw output of the conversion.
The file `stanford/all-parses-aligned.txt.stanford` contains these parses where the word IDs are replaced by codes from `words.tsv`.

`stanford/` also contains `stanford/all-parses-aligned.txt.stanford.depfeatures`, which contains three columns: the first is a word code, the second is the distance between a word and its farthest head, and the third is the number of outstanding dependencies present during a word.

Also including scripts: `align_parses.py`, which aligns the word codes in `words.tsv` with Penn Treebank style parses. Run this with two arguments (the path to `words.tsv` and the path to the Penn Treebank file) to align a Penn Treebank file. Run it with three arguments (path to `words.tsv`, path to a Penn Treebank file, and path to a CoNLL-X file) to align a Universal Dependencies CoNLL-X file.
