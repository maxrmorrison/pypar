###############################################################################
# Phoneme
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
        self._start = start
        self._end = end

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
            abs(self._start - other._start) < 1e-5 and \
            abs(self._end - other._end) < 1e-5

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
        return self._end - self._start

    def end(self):
        """Retrieve the end time of the phoneme in seconds

        Returns
            end : float
                The end time in seconds
        """
        return self._end

    def start(self):
        """Retrieve the start time of the phoneme in seconds

        Returns
            start : float
                The start time in seconds
        """
        return self._start
