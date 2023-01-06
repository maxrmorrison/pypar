import copy
import json
from pathlib import Path

import textgrid

import pypar


###############################################################################
# Alignment representation
###############################################################################


class Alignment:
    """Phoneme alignment

    Arguments
        alignment : string, Path, list[pypar.Word], or dict
            The filename, list of words, or json dict of the alignment

    Parameters
        words : list[pypar.Word]
            The words in the alignment
    """

    def __init__(self, alignment):
        if isinstance(alignment, str):

            # Load alignment from disk
            self._words = self.load(alignment)

        elif isinstance(alignment, Path):

            # Cast and load
            self._words = self.load(str(alignment))

        elif isinstance(alignment, list):
            self._words = alignment

            # Require first word to start at 0 seconds
            self.update(start=0.)

        elif isinstance(alignment, dict):
            self._words = self.parse_json(alignment)

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
        return Alignment(self._words + other.words)

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
            return Alignment(copy.deepcopy(self._words[idx]))

        # Retrieve a single word
        return self._words[idx]

    def __len__(self):
        """Retrieve the number of words

        Returns
            length : int
                The number of words in the alignment
        """
        return len(self._words)

    def __str__(self):
        """Retrieve the text

        Returns
            words : string
                The words in the alignment
        """
        return ' '.join([str(word) for word in self._words
                         if str(word) != pypar.SILENCE])

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
        return self._words[-1].end()

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

        for i in range(0, len(self._words) - len(words) + 1):

            # Get text
            text = str(self._words[i]).lower()

            # Skip silence
            if text == pypar.SILENCE:
                continue

            j, k = 0, 0
            while j < len(words):

                # Compare words
                if text != words[j]:
                    break

                # Increment words
                j += 1
                k += 1
                text = str(self._words[i + k]).lower()

                # skip silence
                while text == pypar.SILENCE:
                    k += 1
                    text = str(self._words[i + k]).lower()

            # Found match; return indices
            if j == len(words):
                return i

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

    def phoneme_bounds(self, sample_rate, hopsize=1):
        """Retrieve the start and end frame index of each phoneme

        Arguments
            sample_rate : int
                The audio sampling rate
            hopsize : int
                The number of samples between successive frames

        Returns
            bounds : list[tuple[int, int]]
                The start and end indices of the phonemes
        """
        bounds = [(p.start(), p.end()) for p in self.phonemes()
                  if str(p) != pypar.SILENCE]
        return [(int(a * sample_rate / hopsize),
                 int(b * sample_rate / hopsize))
                for a, b in bounds]

    def save(self, filename):
        """Save alignment to json

        Arguments
            filename : string
                The location on disk to save the phoneme alignment json
        """
        if isinstance(filename, Path):
            filename = str(filename)
        extension = filename.split('.')[-1]
        if extension == 'json':
            self.save_json(filename)
        elif extension.lower() == 'textgrid':
            self.save_textgrid(filename)
        else:
            raise ValueError(
                f'No save routine for files with extension {extension}')

    def start(self):
        """Retrieve the start time of the alignment in seconds

        Returns
            start : float
                The start time in seconds
        """
        return self._words[0].start()

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

            start = word.end()
            start_phoneme += len(word)

    def words(self):
        """Retrieve the words in the alignment"""
        return self._words

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

    def word_bounds(self, sample_rate, hopsize=1, silences=False):
        """Retrieve the start and end frame index of each word

        Arguments
            sample_rate : int
                The audio sampling rate
            hopsize : int
                The number of samples between successive frames
            silences : bool
                Whether to include silences as words

        Returns
            bounds : list[tuple[int, int]]
                The start and end indices of the words
        """
        words = [
            word for word in self if str(word) != pypar.SILENCE or silences]
        bounds = [(word.start(), word.end()) for word in words]
        return [(int(a * sample_rate / hopsize),
                 int(b * sample_rate / hopsize))
                for a, b in bounds]

    ###########################################################################
    # Utilities
    ###########################################################################

    def json(self):
        """Convert to json format"""
        words = []
        for word in self._words:

            # Convert phonemes to list
            phonemes = [[str(phoneme), phoneme.start(), phoneme.end()]
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
        """Load alignment from file"""
        extension = file.split('.')[-1]
        if extension == 'mlf':
            return self.load_mlf(file)
        if extension == 'json':
            return self.load_json(file)
        if extension.lower() == 'textgrid':
            return self.load_textgrid(file)
        raise ValueError(
            f'No alignment representation for file extension {extension}')

    def load_json(self, filename):
        """Load alignment from json file"""
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
                    words.append(pypar.Word(word, phonemes))
                    phonemes = []

                word = line.word

            # Add a phoneme
            phonemes.append(pypar.Phoneme(line.phoneme, line.start, line.end))

        # Handle last word
        if phonemes:
            words.append(pypar.Word(word, phonemes))

        return words

    def load_textgrid(self, filename):
        """Load from textgrid file"""
        # Load file
        grid = textgrid.TextGrid.fromFile(filename)

        # Get phoneme and word representations
        if 'word' in grid[0].name and 'phon' in grid[1].name:
            word_tier, phon_tier = grid[0], grid[1]
        elif 'phon' in grid[0].name and 'word' in grid[1].name:
            phon_tier, word_tier = grid[0], grid[1]
        else:
            raise ValueError(
                'Cannot determine which TextGrid tiers ' +
                'correspond to words and phonemes')

        # Iterate over words
        words = []
        phon_idx = 0
        for word in word_tier:

            # Get all phonemes for this word
            phonemes = []
            while phon_idx < len(phon_tier) and \
                  phon_tier[phon_idx].maxTime <= word.maxTime:
                phoneme = phon_tier[phon_idx]
                mark = phoneme.mark if phoneme.mark != 'sil' else pypar.SILENCE
                phonemes.append(pypar.Phoneme(mark,
                                              phoneme.minTime,
                                              phoneme.maxTime))
                phon_idx += 1

            # Add finished word
            words.append(pypar.Word(word.mark, phonemes))

        return words

    def parse_json(self, alignment):
        """Construct word list from json representation"""
        words = []
        for word in alignment['words']:
            try:

                # Add a word
                phonemes = [
                    pypar.Phoneme(*phoneme) for phoneme in word['phonemes']]
                words.append(pypar.Word(word['alignedWord'], phonemes))

            except KeyError:

                # Add a silence
                phonemes = [
                    pypar.Phoneme(pypar.SILENCE, word['start'], word['end'])]
                words.append(pypar.Word(pypar.SILENCE, phonemes))

        return words

    def save_json(self, filename):
        """Save alignment as json"""
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(self.json(), file, ensure_ascii=False, indent=4)

    def save_textgrid(self, filename):
        """Save alignment as textgrid"""
        # Construct phoneme tier
        phon_tier = textgrid.IntervalTier('phone', self.start(), self.end())
        for phoneme in self.phonemes():
            mark = 'sil' if str(phoneme) == pypar.SILENCE else str(phoneme)
            phon_tier.add(phoneme.start(), phoneme.end(), mark)

        # Construct word tier
        word_tier = textgrid.IntervalTier('word', self.start(), self.end())
        for word in self:
            word_tier.add(word.start(), word.end(), str(word))

        # Construct textgrid
        grid = textgrid.TextGrid(Path(filename).stem, self.start(), self.end())
        grid.extend([phon_tier, word_tier])

        # Save
        grid.write(filename)

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

                # Extend existing silence if possible
                if str(self[i]) == pypar.SILENCE:
                    self[i][0]._start = start
                else:
                    word = pypar.Word(pypar.SILENCE,
                                    [pypar.Phoneme(pypar.SILENCE, start, end)])
                    self._words.insert(i, word)
                    i += 1

            i += 1
            start = self[i].end()

        # Phoneme gap validation
        for word in self:
            word.validate()


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
