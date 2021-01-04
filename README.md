# Python phoneme alignment representation

Phoneme alignment representation for speech tasks. This repo does not perform
forced phoneme alignment, but provides an interface for working with the
resulting alignment of a forced aligner such as
[`pyfoal`](https://github.com/maxrmorrison/pyfoal).


### Installation

`pip install pypar`


### Usage

##### Creating an alignment

If you already have the alignment saved to a `json` or `mlf` file, pass the
name of the file.

```python
alignment = pypar.Alignment(file)
```

Alignments can be created manually from `Word` and `Phoneme` objects.

```python
phonemes = [pypar.Phoneme('DH', 0., .03), pypar.Phoneme('AH0', .03, .06)]
words = [pypar.Word('THE', phonemes)]
alignment = pypar.Alignment(words)
```

You can create a new alignment from existing alignments via slicing and
concatenation.

```python
# Slice
first_two_words = alignment[:2]

# Concatenate
alignment_with_repeat = first_two_words + alignment
```


##### Accessing words and phonemes

To retrieve a list of words in the alignment, use `alignment.words()`.
To retrieve a list of phonemes, use `alignment.phonemes()`. The `Alignment`,
`Word`, and `Phoneme` objects all define `.start()`, `.end()`, and
`.duration()` methods, which return the start time, end time, and duration,
respectively. All times are given in units of seconds. These objects also
define equality checks via `==` and casting to string with `str()`.

To access a word or phoneme at a specific time, use `alignment.word_at_time`
or `alignment.phoneme_at_time`.

To retrieve the frame indices of the start and end of a word or phoneme, use
`alignment.word_bounds` or `alignment.phoneme_bounds`.


##### Saving an alignment

To save an alignment to disk, use `alignment.save(file)`, where `file` is the
desired filename. `pypar` currently supports saving as a `json` file.
