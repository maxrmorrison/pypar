import copy
import json

import numpy as np


__all__ = ['SILENCE',
           'Alignment',
           'Phoneme',
           'Word',
           'rate_difference_per_phoneme',
           'rate_difference_per_frame']


###############################################################################
# Constants
###############################################################################


SILENCE = 'sp'


###############################################################################
# Alignment representation
###############################################################################


class Alignment:
    """Phoneme alignment

    Arguments
        alignment : string, list[pypar.Word], or dict
            The filename, list of words, or json dict of the alignment

    Parameters
        words : list[pypar.Word]
            The words in the alignment
    """

    def __init__(self, alignment):
        if isinstance(alignment, str):

            # Load alignment from disk
            self.words = self.load(alignment)

        elif isinstance(alignment, list):
            self.words = alignment

            # Require first word to start at 0 seconds
            self.update(start=0.)

        elif isinstance(alignment, dict):
            self.words = self.parse_json(alignment)

        # Ensure there are no gaps (by filling with silence)
        self.validate()

    def __add__(self, other):
        """Add alignments by concatenation

        Arguments
            other : pypar.Alignment
                The alignment to compare to

        Returns
            alignment : pypar.Alignment
                The concatenated alignment
        """
        # Don't change original
        other = copy.deepcopy(other)

        # Move start time of other to end of self
        other.update(start=self.end())

        # Concatenate word lists
        return Alignment(self.words + other.words)

    def __eq__(self, other):
        """Equality comparison for alignments

        Arguments
            other : pypar.Alignment
                The alignment to compare to

        Returns
            equal : bool
                Whether the alignments are equal
        """
        return \
            len(self) == len(other) and \
            all(word == other_word for word, other_word in zip(self, other))

    def __getitem__(self, idx):
        """Retrieve the idxth word

        Arguments
            idx : int or slice
                The index of the word to retrieve

        Returns
            word : pypar.Word
                The word at index idx
        """
        if isinstance(idx, slice):

            # Slice into word list
            return Alignment(copy.deepcopy(self.words[idx]))

        # Retrieve a single word
        return self.words[idx]

    def __len__(self):
        """Retrieve the number of words

        Returns
            length : int
                The number of words in the alignment
        """
        return len(self.words)

    def __setitem__(self, idx, word):
        """Update the idxth word

        Arguments
            idx : int
                The index of the word to update
            word : pypar.Word
                The new word
        """
        self.words[idx] = word

    def __str__(self):
        """Retrieve the text

        Returns
            words : string
                The words in the alignment
        """
        return ' '.join([str(word) for word in self.words
                         if str(word) != SILENCE])

    def duration(self):
        """Retrieve the duration of the alignment in seconds

        Returns
            duration : float
                The duration in seconds
        """
        return self.end() - self.start()

    def end(self):
        """Retrieve the end time of the alignment in seconds

        Returns
            end : float
                The end time in seconds
        """
        return self.words[-1].end()

    def find(self, words):
        """Find the words in the alignment

        Arguments
            words : string
                The words to find

        Returns
            index : int
                The index of the start of the words or -1 if not found
        """
        # Split at spaces
        words = words.split(' ')

        for i in range(0, len(self.words) - len(words) + 1):

            # Get text
            text = str(self.words[i]).lower()

            # Skip silence
            if text == SILENCE:
                continue

            j, k = 0, 0
            while j < len(words):

                # Compare words
                if text != words[j]:
                    break

                # Increment words
                j += 1
                k += 1
                text = str(self.words[i + k]).lower()

                # skip silence
                while text == SILENCE:
                    k += 1
                    text = str(self.words[i + k]).lower()

            # Found match; return indices
            if j == len(words):
                return i, i + k

        # No match
        return -1

    def phonemes(self):
        """Retrieve the phonemes in the alignment

        Returns
            phonemes : list[pypar.Phoneme]
                The phonemes in the alignment
        """
        return [phoneme for word in self for phoneme in word]

    def phoneme_at_time(self, time):
        """Retrieve the phoneme spoken at specified time

        Arguments
            time : float
                Time in seconds

        Returns
            phoneme : pypar.Phoneme or None
                The phoneme at the given time
        """
        word = self.word_at_time(time)
        return word.phoneme_at_time(time) if word else None

    def phoneme_bounds(self, sample_rate, hopsize):
        """Retrieve the start and end frame index of each phoneme

        Arguments
            sample_rate : int
                The audio sampling rate
            hopsize : float
                The size of the analysis window in samples

        Returns
            bounds : list[tuple[int, int]]
                The start and end indices of the phonemes
        """
        bounds = [(p.start, p.end) for p in self.phonemes()
                  if str(p) != SILENCE]
        return [(int(a * sample_rate / hopsize),
                 int(b * sample_rate / hopsize))
                for a, b in bounds]

    def save(self, filename):
        """Save alignment to json

        Arguments
            filename : string
                The location on disk to save the phoneme alignment json
        """
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(self.json(), file, ensure_ascii=False, indent=4)

    def replace(self, start_idx, end_idx, words):
        """Replaces words between start_idx and end_idx with words

        Arguments
            start_idx : int
                The index of the first word to replace
            end_idx : int
                One past the index of the last word to replace
            words : list[pypar.Word]
                The words to be inserted
        """
        # Don't change alignment start time
        start = self.start()

        # Replace words
        self.words = self.words[:start_idx] + \
                     copy.deepcopy(words) + \
                     self.words[end_idx:]

        # Fix phoneme start and end times
        start_phoneme = sum(len(word) for word in self.words[:start_idx])
        self.update(start_phoneme, start=start)

    def start(self):
        """Retrieve the start time of the alignment in seconds

        Returns
            start : float
                The start time in seconds
        """
        return self.words[0].start()

    def update(self, idx=0, durations=None, start=None):
        """Update alignment starting from phoneme index idx

        Arguments
            idx : int
                The index of the first phoneme whose duration is being updated
            durations : list[float] or None
                The new phoneme durations, starting from idx
            start : float or None
                The start time of the alignment
        """
        # If durations are not given, just update phoneme start and end times
        durations = [] if durations is None else durations

        # Word start time (in seconds) and phoneme start index
        start = self.start() if start is None else start
        start_phoneme = 0

        # Update each word
        for word in self:
            end_phoneme = start_phoneme + len(word)

            # Update phoneme alignment of this word
            word = self.update_word(
                word, idx, durations, start, start_phoneme, end_phoneme)

            start += word.duration()
            start_phoneme += len(word)

    def word_at_time(self, time):
        """Retrieve the word spoken at specified time

        Arguments
            time : float
                Time in seconds

        Returns
            word : pypar.Word or None
                The word spoken at the specified time
        """
        for word in self:
            if word.start() <= time <= word.end():
                return word
        return None

    def word_bounds(self, sample_rate, hopsize):
        """Retrieve the start and end frame index of each word

        Arguments
            sample_rate : int
                The audio sampling rate
            hopsize : float
                The size of the analysis window in samples

        Returns
            bounds : list[tuple[int, int]]
                The start and end indices of the words
        """
        bounds = [(word.start(), word.end()) for word in self
                  if str(word) != SILENCE]
        return [(int(a * sample_rate / hopsize),
                 int(b * sample_rate / hopsize))
                for a, b in bounds]

    ###########################################################################
    # Utilities
    ###########################################################################

    def json(self):
        """Convert to json format"""
        words = []
        for word in self.words:

            # Convert phonemes to list
            phonemes = [[str(phoneme), phoneme.start, phoneme.end]
                        for phoneme in word]

            # Convert word to dict format
            words.append({'alignedWord': str(word),
                          'start': word.start(),
                          'end': word.end(),
                          'phonemes': phonemes})

        return {'words': words}

    def line_is_valid(self, line):
        """Check if a line of a mlf file represents a phoneme"""
        line = line.strip().split()
        if not line:
            return False
        return len(line) in [4, 5]

    def load(self, file):
        """Load the mlf file and format into words"""
        extension = file.split('.')[-1]
        if extension == 'mlf':
            return self.load_mlf(file)
        if extension == 'json':
            return self.load_json(file)
        raise ValueError(
            f'No alignment representation for file extension {extension}')

    def load_json(self, filename):
        """Load from json file"""
        # Load from json file
        with open(filename) as file:
            return self.parse_json(json.load(file))

    def load_mlf(self, filename):
        """Load from mlf file"""
        # Load file from disk
        with open(filename) as file:
            # Read in phoneme alignment
            lines = [Line(line) for line in file.readlines()
                     if self.line_is_valid(line)]

            # Remove silence tokens with 0 duration
            lines = [line for line in lines if line.start < line.end]

        # Extract words and phonemes
        phonemes = []
        words = []
        for line in lines:

            # Start new word
            if line.word is not None:

                # Add word that just finished
                if phonemes:
                    words.append(Word(word, phonemes))
                    phonemes = []

                word = line.word

            # Add a phoneme
            phonemes.append(Phoneme(line.phoneme, line.start, line.end))

        # Handle last word
        if phonemes:
            words.append(Word(word, phonemes))

        return words

    def parse_json(self, alignment):
        """Construct word list from json representation"""
        words = []
        for word in alignment['words']:
            try:

                # Add a word
                phonemes = [Phoneme(*phoneme) for phoneme in word['phonemes']]
                words.append(Word(word['alignedWord'], phonemes))

            except KeyError:

                # Add a silence
                phonemes = [Phoneme(SILENCE, word['start'], word['end'])]
                words.append(Word(SILENCE, phonemes))

        return words

    def update_word(self,
                    word,
                    idx,
                    durations,
                    start,
                    start_phoneme,
                    end_phoneme):
        """Update the phoneme alignment of one word"""
        # All phonemes beyond (and including) idx must be updated
        if end_phoneme > idx:

            # Retrieve current phoneme durations for word
            word_durations = [phoneme.duration() for phoneme in word]

            # The first len(durations) phonemes use new durations
            if start_phoneme - idx < len(durations) and end_phoneme - idx > 0:

                # Get indices into durations for copy/paste operation
                src_start_idx = max(0, start_phoneme - idx)
                src_end_idx = min(len(durations), end_phoneme - idx)
                src = durations[src_start_idx:src_end_idx]

                # Case 1: replace all phonemes in word
                if len(src) == len(word_durations):
                    dst_start_idx, dst_end_idx = 0, len(word_durations)

                # Case 2: replace right-most phonemes in word
                elif idx > start_phoneme and len(src) == end_phoneme - idx:
                    dst_start_idx = len(word_durations) - len(src)
                    dst_end_idx = len(word_durations)

                # Case 3: replace left-most phonemes in word
                elif idx <= start_phoneme:
                    dst_start_idx = 0
                    dst_end_idx = len(word_durations) - len(src)

                # Case 4: replace phonemes in center of word
                else:
                    dst_start_idx = -(start_phoneme - idx)
                    dst_end_idx = dst_start_idx + len(src)

                # Perform copy/paste on duration vector
                word_durations[dst_start_idx:dst_end_idx] = \
                    durations[src_start_idx:src_end_idx]

            # Get new durations for word
            word.update(start, word_durations)

        return word

    def validate(self):
        """Ensures that adjacent start/stop times are valid by adding silence"""
        i = 0
        start = 0.
        while i < len(self) - 1:

            # Get start and end times between words
            end = self[i].start()

            # Patch gap with silence
            if end - start > 1e-3:
                word = Word(SILENCE, [Phoneme(SILENCE, start, end)])
                self.words.insert(i, word)
                i += 1

            i += 1
            start = self[i].end()

        # Phoneme gap validation
        for word in self:
            word.validate()


###############################################################################
# Phoneme representation
###############################################################################


class Phoneme:
    """Aligned phoneme representation

    Arguments
        phoneme : string
            The phoneme
        start : float
            The start time in seconds
        end : float
            The end time in seconds

    Parameters
        phoneme : string
            The phoneme
        start : float
            The start time in seconds
        end : float
            The end time in seconds
    """

    def __init__(self, phoneme, start, end):
        self.phoneme = phoneme
        self.start = start
        self.end = end

    def __eq__(self, other):
        """Equality comparison for phonemes

        Arguments
            other : pypar.Phoneme
                The phoneme to compare to

        Returns
            equal : bool
                Whether the phonemes are equal
        """
        return \
            str(self) == str(other) and \
            abs(self.start - other.start) < 1e-5 and \
            abs(self.end - other.end) < 1e-5

    def __str__(self):
        """Retrieve the phoneme text

        Returns
            phoneme : string
                The phoneme
        """
        return self.phoneme

    def duration(self):
        """Retrieve the phoneme duration

        Returns
            duration : float
                The duration in seconds
        """
        return self.end - self.start


###############################################################################
# Word representation
###############################################################################


class Word:
    """Aligned word represenatation

    Arguments
        word : string
            The word
        phonemes : list[pypar.Phoneme]
            The phonemes in the word

    Parameters
        word : string
            The word
        phonemes : list[pypar.Phoneme]
            The phonemes in the word
    """

    def __init__(self, word, phonemes):
        self.word = word
        self.phonemes = phonemes

    def __eq__(self, other):
        """Equality comparison for words

        Arguments
            other : pypar.Word
                The word to compare to

        Returns
            equal : bool
                Whether the words are the same
        """
        return \
            str(self) == str(other) and \
            len(self) == len(other) and \
            all(phoneme == other_phoneme
                for phoneme, other_phoneme in zip(self, other))

    def __getitem__(self, idx):
        """Retrieve the idxth phoneme

        Arguments
            idx : int
                The index of the phoneme to retrieve

        Returns
            phoneme : pypar.Phoneme
                The phoneme at index idx
        """
        return self.phonemes[idx]

    def __setitem__(self, idx, phoneme):
        """Change the idxth phoneme

        Arguments
            idx : int
                The index of the phoneme to update
            phoneme : pypar.Phoneme
                The new phoneme
        """
        self.phonemes[idx] = phoneme

    def __len__(self):
        """Retrieve the number of phonemes

        Returns
            length : int
                The number of phonemes
        """
        return len(self.phonemes)

    def __str__(self):
        """Retrieve the word text

        Returns
            word : string
                The word text
        """
        return self.word

    def duration(self):
        """Retrieve the word duration in seconds

        Returns
            duration : float
                The duration in seconds
        """
        return self.end() - self.start()

    def end(self):
        """Retrieve the end time of the word in seconds

        Returns
            end : float
                The end time in seconds
        """
        return self.phonemes[-1].end

    def phoneme_at_time(self, time):
        """Retrieve the phoneme at the specified time"""
        for phoneme in self.phonemes:
            if phoneme.start <= time <= phoneme.end:
                return phoneme
        return None

    def start(self):
        """Retrieve the start time of the word in seconds

        Returns
            start : float
                The start time in seconds
        """
        return self.phonemes[0].start

    def update(self, start, durations=None):
        """Update the word with new start time and phoneme durations

        Arguments
            start : float
                The new start time of the word
            durations : list[float] or None
                The new phoneme durations
        """
        # Use current durations if None provided
        if durations is None:
            durations = [phoneme.duration for phoneme in self.phonemes]

        # Update phonemes
        phoneme_start = start
        for phoneme, duration in zip(self.phonemes, durations):
            phoneme.start = phoneme_start
            phoneme.end = phoneme.start + duration
            phoneme_start += duration

    ###########################################################################
    # Utilities
    ###########################################################################

    def validate(self):
        """Ensures that adjacent start/end times are valid by adding silence"""
        i = 0
        while i < len(self) - 1:

            # Get start and end times between phonemes
            start = self[i].end
            end = self[i + 1].start

            # Patch gap with silence
            if end - start > 1e-4:
                self.phonemes.insert(i + 1, Phoneme(SILENCE, start, end))
                i += 1

            i += 1


###############################################################################
# Utilities
###############################################################################


class Line:
    """One line of a HTK mlf file"""

    def __init__(self, line):
        line = line.strip().split()

        if len(line) == 4:
            start, end, self.phoneme, _ = line
            self.word = None
        else:
            start, end, self.phoneme, _, self.word = line

        self.start = float(start) / 10000000.
        self.end = float(end) / 10000000.


def phoneme_tuple(phoneme):
    """Convert phoneme to hashable tuple representation

    Arguments
        phoneme - The phoneme to convert

    Returns
        tuple(float, float, string)
            The phoneme represented as a tuple
    """
    return (phoneme.start, phoneme.end, str(phoneme))


def rate_difference_per_frame(alignment_a, alignment_b, hopsize):
    """Compute the per-frame rate difference between alignments A and B

    Arguments
        alignment_a : Alignment
            The source alignment
        alignment_b : Alignment
            The target alignment
        hopsize : float
            The hopsize in seconds

    Returns
        rates : list[float]
            The frame-wise relative speed of alignment B to alignment A
    """
    # Create dict mapping phoneme to relative rate
    rates_per_phoneme = rate_difference_per_phoneme(alignment_a, alignment_b)
    dict_keys = [phoneme_tuple(phoneme) for phoneme in alignment_a.phonemes()]
    rate_map = dict(zip(dict_keys, rates_per_phoneme))

    # Query the dict every hopsize seconds
    frames = 1 + int(alignment_a.end() / hopsize + 1e-4)
    return [rate_map[phoneme_tuple(alignment_a.phoneme_at_time(t))]
            for t in np.linspace(0., alignment_a.end(), frames)]


def rate_difference_per_phoneme(alignment_a, alignment_b):
    """Compute the per-phoneme rate difference between alignments A and B

    Arguments
        alignment_a : Alignment
            The source alignment
        alignment_b : Alignment
            The target alignment

    Returns
        rates : list[float]
            The phoneme-wise relative speed of alignment B to alignment A
    """
    iterator = zip(alignment_a.phonemes(), alignment_b.phonemes())
    return [target.duration() / source.duration()
            for source, target in iterator]
