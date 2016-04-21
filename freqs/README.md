# Natural Stories Frequencies

These are conditional frequencies for each word in the corpus in the Google Books English corpus, summing over years from 1990 to the present.
The script used to extract these frequencies is `scripts/get_freqs.py`.

Each file `freqs-N.tsv` contains columns:

1. Token code, as in `words.tsv`,
2. N-gram order,
3. Token,
4. Frequency of the N-gram consisting of the current token and the previous N-1 `word` tokens up to the nearest sentence boundary,
5. Frequency of the (N-1)-gram consisting of the previous N-1 `word` tokens up to the nearest sentence boundary.

The MLE estimate of the conditional N-gram probability of a token in its context can be found by dividing column 4 by column 5.
