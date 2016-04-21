The original files, corrected by Laura, are in the directories docx/
and txt/.

The directory penn/ contains parses with some further corrections;
these are the most up-to-date parses. The file all-parses.txt.penn
just contains the parses. The file all-parses-aligned.txt.penn
contains the parses with each word tagged with its code as defined in
words.tsv.

penn/ also contains a file all-parses-aligned-txt.penn.consfeatures,
which contains two columns: the first is a word code, the second is
the number of constituents ended by that word.

The directory stanford/ contains the parses converted into dependency
format using the Stanford Parser. The file all-parses.txt.stanford
contains only these parses. The file all-parses-aligned.txt.stanford
contains these parses where the word IDs are replaced by codes from
words.tsv.

stanford/ also contains a all-parses-aligned.txt.stanford.depfeatures,
which contains three columns: the first is a word code, the second is
the distance between a word and its farthest head, and the third is
the number of outstanding dependencies present during a word.

Also including scripts: align_parses.py, which aligns the word codes
in words.tsv with Penn and Stanford parses, depfeatures.py which
calculates the depfeatures file, and consfeatures.py which calculates
the consfeatures file.
