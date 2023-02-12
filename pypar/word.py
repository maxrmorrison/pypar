import pypar


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
        return self.phonemes[-1].end()

    def phoneme_at_time(self, time):
        """Retrieve the phoneme at the specified time"""
        for phoneme in self.phonemes:
            if phoneme.start() <= time <= phoneme.end():
                return phoneme
        return None

    def start(self):
        """Retrieve the start time of the word in seconds

        Returns
            start : float
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
