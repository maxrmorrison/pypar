from typing import List, Optional

import pypar


###############################################################################
# Word representation
###############################################################################


class Word:
    """Aligned word represenatation"""

    def __init__(self, word: str, phonemes: List[pypar.Phoneme]) -> None:
        """Create word

        Arguments
            word
                The word
            phonemes
                The phonemes in the word
        """
        self.word = word
        self.phonemes = phonemes

    def __eq__(self, other) -> bool:
        """Equality comparison for words

        Arguments
            other
                The word to compare to

        Returns
            Whether the words are the same
        """
        return \
            str(self) == str(other) and \
            len(self) == len(other) and \
            all(phoneme == other_phoneme
                for phoneme, other_phoneme in zip(self, other))

    def __getitem__(self, idx: int) -> pypar.Phoneme:
        """Retrieve the idxth phoneme

        Arguments
            idx
                The index of the phoneme to retrieve

        Returns
            The phoneme at index idx
        """
        return self.phonemes[idx]

    def __len__(self) -> int:
        """Retrieve the number of phonemes

        Returns
            The number of phonemes
        """
        return len(self.phonemes)

    def __str__(self) -> str:
        """Retrieve the word text

        Returns
            The word text
        """
        return self.word

    def duration(self) -> float:
        """Retrieve the word duration in seconds

        Returns
            The duration in seconds
        """
        return self.end() - self.start()

    def end(self) -> float:
        """Retrieve the end time of the word in seconds

        Returns
            The end time in seconds
        """
        return self.phonemes[-1].end()

    def phoneme_at_time(self, time: float) -> Optional[pypar.Phoneme]:
        """Retrieve the phoneme at the specified time

        Arguments
            time
                Time in seconds

        Returns
            The phoneme at the given time (or None if time is out of bounds)
        """
        for phoneme in self.phonemes:
            if phoneme.start() <= time <= phoneme.end():
                return phoneme
        return None

    def start(self) -> float:
        """Retrieve the start time of the word in seconds

        Returns
            The start time in seconds
        """
        return self.phonemes[0].start()

    ###########################################################################
    # Utilities
    ###########################################################################

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
            durations = [phoneme.duration() for phoneme in self.phonemes]

        # Update phonemes
        phoneme_start = start
        for phoneme, duration in zip(self.phonemes, durations):
            phoneme._start = phoneme_start
            phoneme._end = phoneme_start + duration
            phoneme_start = phoneme._end

    def validate(self):
        """Ensures that adjacent start/end times are valid by adding silence"""
        i = 0
        while i < len(self) - 1:

            # Get start and end times between phonemes
            start = self[i].end()
            end = self[i + 1].start()

            # Patch gap with silence
            if end - start > 1e-4:
                phoneme = pypar.Phoneme(pypar.SILENCE, start, end)
                self.phonemes.insert(i + 1, phoneme)
                i += 1

            i += 1
