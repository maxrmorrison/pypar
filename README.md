<h1 align="center">Python phoneme alignment representation</h1>
<div align="center">

[![PyPI](https://img.shields.io/pypi/v/pypar.svg)](https://pypi.python.org/pypi/pypar)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/pypar)](https://pepy.tech/project/pypar)

`pip install pypar`
</div>

Word and phoneme alignment representation for speech tasks. This repo does
not perform forced word or phoneme alignment, but provides an interface
for working with the resulting alignment of a forced aligner, such as
[`pyfoal`](https://github.com/maxrmorrison/pyfoal), or a manual alignment.


## Table of contents

- [Usage](#usage)
    * [Creating alignments](#creating-aligments)
    * [Accessing words and phonemes](#accessing-words-and-phonemes)
    * [Saving alignments](#saving-alignments)
- [Application programming interface (API)](#application-programming-interface-api)
    * [`pypar.Alignment`](#pyparalignment)
        * [`pypar.Alignment.__init__`](#pyparalignment__init__)
        * [`pypar.Alignment.__add__`](#pyparalignment__add__)
        * [`pypar.Alignment.__eq__`](#pyparalignment__eq__)
        * [`pypar.Alignment.__getitem__`](#pyparalignment__getitem__)
        * [`pypar.Alignment.__len__`](#pyparalignment__len__)
        * [`pypar.Alignment.__str__`](#pyparalignment__str__)
        * [`pypar.Alignment.duration`](#pyparalignmentduration)
        * [`pypar.Alignment.end`](#pyparalignmentend)
        * [`pypar.Alignment.find`](#pyparalignmentfind)
        * [`pypar.Alignment.framewise_phoneme_indices`](#pyparalignmentframewise_phoneme_indices)
        * [`pypar.Alignment.phonemes`](#pyparalignmentphonemes)
        * [`pypar.Alignment.phoneme_at_time`](#pyparalignmentphoneme_at_time)
        * [`pypar.Alignment.phoneme_bounds`](#pyparalignmentphoneme_bounds)
        * [`pypar.Alignment.save`](#pyparalignmentsave)
        * [`pypar.Alignment.start`](#pyparalignmentstart)
        * [`pypar.Alignment.update`](#pyparalignmentupdate)
        * [`pypar.Alignment.words`](#pyparalignmentwords)
        * [`pypar.Alignment.word_bounds`](#pyparalignmentword_bounds)
    * [`pypar.Phoneme`](#pyparphoneme)
        * [`pypar.Phoneme.__init__`](#pyparphoneme__init__)
        * [`pypar.Phoneme.__eq__`](#pyparphoneme__eq__)
        * [`pypar.Phoneme.__str__`](#pyparphoneme__str__)
        * [`pypar.Phoneme.duration`](#pyparphonemeduration)
        * [`pypar.Phoneme.end`](#pyparphonemeend)
        * [`pypar.Phoneme.start`](#pyparphonemestart)
    * [`pypar.Word`](#pyparword)
        * [`pypar.Word.__init__`](#pyparword__init__)
        * [`pypar.Word.__eq__`](#pyparword__eq__)
        * [`pypar.Word.__getitem__`](#pyparword__getitem__)
        * [`pypar.Word.__len__`](#pyparword__len__)
        * [`pypar.Word.__str__`](#pyparword__str__)
        * [`pypar.Word.duration`](#pyparwordduration)
        * [`pypar.Word.end`](#pyparwordend)
        * [`pypar.Word.phoneme_at_time`](#pyparwordphoneme_at_time)
        * [`pypar.Word.start`](#pyparwordstart)
- [Tests](#tests)

## Usage

### Creating alignments

If you already have the alignment saved to a `json`, `mlf`, or `TextGrid`
file, pass the name of the file. Valid examples of each format can be found in
`test/assets/`.

```python
alignment = pypar.Alignment(file)
```

Alignments can be created manually from `Word` and `Phoneme` objects. Start and
end times are given in seconds.

```python
# Create a word from phonemes
word = pypar.Word(
    'THE',
    [pypar.Phoneme('DH', 0., .03), pypar.Phoneme('AH0', .03, .06)])

# Create a silence
silence = pypar.Word(pypar.SILENCE, pypar.Phoneme(pypar.SILENCE, .06, .16))

# Make an alignment
alignment = pypar.Alignment([word, silence])
```

You can create a new alignment from existing alignments via slicing and
concatenation.

```python
# Slice
first_two_words = alignment[:2]

# Concatenate
alignment_with_repeat = first_two_words + alignment
```


### Accessing words and phonemes

To retrieve a list of words in the alignment, use `alignment.words()`.
To retrieve a list of phonemes, use `alignment.phonemes()`. The `Alignment`,
`Word`, and `Phoneme` objects all define `.start()`, `.end()`, and
`.duration()` methods, which return the start time, end time, and duration,
respectively. All times are given in units of seconds. These objects also
define equality checks via `==`, casting to string with `str()`, and iteration
as follows.

```python
# Iterate over words
for word in alignment:

    # Access start and end times
    assert word.duration() == word.end() - word.start()

    # Iterate over phonemes in word
    for phoneme in word:

        # Access string representation
        assert isinstance(str(phoneme), str)
```

To access a word or phoneme at a specific time, pass the time in seconds to
`alignment.word_at_time` or `alignment.phoneme_at_time`.

To retrieve the frame indices of the start and end of a word or phoneme, pass
the audio sampling rate and hopsize (in samples) to `alignment.word_bounds` or
`alignment.phoneme_bounds`.


### Saving alignments

To save an alignment to disk, use `alignment.save(file)`, where `file` is the
desired filename. `pypar` currently supports saving as a `json` or `TextGrid`
file.


## Application programming interface (API)

### `pypar.Alignment`

#### `pypar.Alignment.__init__`

```python
def __init__(
    self,
    alignment: Union[str, bytes, os.PathLike, List[pypar.Word], dict]
) -> None:
    """Create alignment

    Arguments
        alignment
            The filename, list of words, or json dict of the alignment
    """
```


#### `pypar.Alignment.__add__`

```python
def __add__(self, other):
    """Add alignments by concatenation

    Arguments
        other
            The alignment to compare to

    Returns
        The concatenated alignment
    """
```


#### `pypar.Alignment.__eq__`

```python
def __eq__(self, other) -> bool:
    """Equality comparison for alignments

    Arguments
        other
            The alignment to compare to

    Returns
        Whether the alignments are equal
    """
```


#### `pypar.Alignment.__getitem__`

```python
def __getitem__(self, idx: Union[int, slice]) -> pypar.Word:
    """Retrieve the idxth word

    Arguments
        idx
            The index of the word to retrieve

    Returns
        The word at index idx
    """
```


#### `pypar.Alignment.__len__`

```python
def __len__(self) -> int:
    """Retrieve the number of words

    Returns
        The number of words in the alignment
    """
```


#### `pypar.Alignment.__str__`

```python
def __str__(self) -> str:
    """Retrieve the text

    Returns
        The words in the alignment separated by spaces
    """
```


#### `pypar.Alignment.duration`

```python
def duration(self) -> float:
    """Retrieve the duration of the alignment in seconds

    Returns
        The duration in seconds
    """
```


#### `pypar.Alignment.end`

```python
def end(self) -> float:
    """Retrieve the end time of the alignment in seconds

    Returns
        The end time in seconds
    """
```


#### `pypar.Alignment.framewise_phoneme_indices`

```python
def framewise_phoneme_indices(
    self,
    phoneme_map: Dict[str, int],
    hopsize: float,
    times: Optional[List[float]] = None
) -> List[int]:
    """Convert alignment to phoneme indices at regular temporal interval

    Arguments
        phoneme_map
            Mapping from phonemes to indices
        hopsize
            Temporal interval between frames in seconds
        times
            Specified times in seconds to sample phonemes
    """
```


#### `pypar.Alignment.find`

```python
def find(self, words: str) -> int:
    """Find the words in the alignment

    Arguments
        words
            The words to find

    Returns
        The index of the start of the words or -1 if not found
    """
```


#### `pypar.Alignment.phonemes`

```python
def phonemes(self) -> List[pypar.Phoneme]:
    """Retrieve the phonemes in the alignment

    Returns
        The phonemes in the alignment
    """
```


#### `pypar.Alignment.phoneme_at_time`

```python
def phoneme_at_time(self, time: float) -> Optional[pypar.Phoneme]:
    """Retrieve the phoneme spoken at specified time

    Arguments
        time
            Time in seconds

    Returns
        The phoneme at the given time (or None if time is out of bounds)
    """
```


#### `pypar.Alignment.phoneme_bounds`

```python
def phoneme_bounds(
    self,
    sample_rate: int,
    hopsize: int = 1
) -> List[Tuple[int, int]]:
    """Retrieve the start and end frame index of each phoneme

    Arguments
        sample_rate
            The audio sampling rate
        hopsize
            The number of samples between successive frames

    Returns
        The start and end indices of the phonemes
    """
```


#### `pypar.Alignment.save`

```python
def save(self, filename: Union[str, bytes, os.PathLike]) -> None:
    """Save alignment to json

    Arguments
        filename
            The location on disk to save the phoneme alignment json
    """
```


#### `pypar.Alignment.start`

```python
def start(self) -> float:
    """Retrieve the start time of the alignment in seconds

    Returns
        The start time in seconds
    """
```


#### `pypar.Alignment.update`

```python
def update(
    self,
    idx: int = 0,
    durations: Optional[List[float]] = None,
    start: Optional[float] = None
) -> None:
    """Update alignment starting from phoneme index idx

    Arguments
        idx
            The index of the first phoneme whose duration is being updated
        durations
            The new phoneme durations, starting from idx
        start
            The start time of the alignment
    """
```


#### `pypar.Alignment.words`

```python
def words(self) -> List[pypar.Word]:
    """Retrieve the words in the alignment

    Returns
        The words in the alignment
    """
```


#### `pypar.Alignment.word_bounds`

```python
def word_at_time(self, time: float) -> Optional[pypar.Word]:
    """Retrieve the word spoken at specified time

    Arguments
        time
            Time in seconds

    Returns
        The word spoken at the specified time
    """
```


### `pypar.Phoneme`

#### `pypar.Phoneme.__init__`

```python
def __init__(self, phoneme: str, start: float, end: float) -> None:
    """Create phoneme

    Arguments
        phoneme
            The phoneme
        start
            The start time in seconds
        end
            The end time in seconds
    """
```


#### `pypar.Phoneme.__eq__`

```python
def __eq__(self, other) -> bool:
    """Equality comparison for phonemes

    Arguments
        other
            The phoneme to compare to

    Returns
        Whether the phonemes are equal
    """
```


#### `pypar.Phoneme.__str__`

```python
def __str__(self) -> str:
    """Retrieve the phoneme text

    Returns
        The phoneme
    """
```


#### `pypar.Phoneme.duration`

```python
def duration(self) -> float:
    """Retrieve the phoneme duration

    Returns
        The duration in seconds
    """
```


#### `pypar.Phoneme.end`

```python
def end(self) -> float:
    """Retrieve the end time of the phoneme in seconds

    Returns
        The end time in seconds
    """
```


#### `pypar.Phoneme.start`

```python
def start(self) -> float:
    """Retrieve the start time of the phoneme in seconds

    Returns
        The start time in seconds
    """
```


### `pypar.Word`

#### `pypar.Word.__init__`

```python
def __init__(self, word: str, phonemes: List[pypar.Phoneme]) -> None:
    """Create word

    Arguments
        word
            The word
        phonemes
            The phonemes in the word
    """
```


#### `pypar.Word.__eq__`

```python
def __eq__(self, other) -> bool:
    """Equality comparison for words

    Arguments
        other
            The word to compare to

    Returns
        Whether the words are the same
    """
```


#### `pypar.Word.__getitem__`

```python
def __getitem__(self, idx: int) -> pypar.Phoneme:
    """Retrieve the idxth phoneme

    Arguments
        idx
            The index of the phoneme to retrieve

    Returns
        The phoneme at index idx
    """
```


#### `pypar.Word.__len__`

```python
def __len__(self) -> int:
    """Retrieve the number of phonemes

    Returns
        The number of phonemes
    """
```


#### `pypar.Word.__str__`

```python
def __str__(self) -> str:
    """Retrieve the word text

    Returns
        The word text
    """
```


#### `pypar.Word.duration`

```python
def duration(self) -> float:
    """Retrieve the word duration in seconds

    Returns
        The duration in seconds
    """
```


#### `pypar.Word.end`

```python
def end(self) -> float:
    """Retrieve the end time of the word in seconds

    Returns
        The end time in seconds
    """
```


#### `pypar.Word.phoneme_at_time`

```python
def phoneme_at_time(self, time: float) -> Optional[pypar.Phoneme]:
    """Retrieve the phoneme at the specified time

    Arguments
        time
            Time in seconds

    Returns
        The phoneme at the given time (or None if time is out of bounds)
    """
```


#### `pypar.Word.start`

```python
    def start(self) -> float:
        """Retrieve the start time of the word in seconds

        Returns
            The start time in seconds
        """
```


## Tests

Tests can be run as follows.

```
pip install pytest
pytest
```
