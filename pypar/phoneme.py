###############################################################################
# Phoneme
###############################################################################


class Phoneme:
    """Aligned phoneme representation"""

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
        self.phoneme = phoneme
        self._start = start
        self._end = end

    def __eq__(self, other) -> bool:
        """Equality comparison for phonemes

        Arguments
            other
                The phoneme to compare to

        Returns
            Whether the phonemes are equal
        """
        return \
            str(self) == str(other) and \
            abs(self._start - other._start) < 1e-5 and \
            abs(self._end - other._end) < 1e-5

    def __str__(self) -> str:
        """Retrieve the phoneme text

        Returns
            The phoneme
        """
        return self.phoneme

    def duration(self) -> float:
        """Retrieve the phoneme duration

        Returns
            The duration in seconds
        """
        return self._end - self._start

    def end(self) -> float:
        """Retrieve the end time of the phoneme in seconds

        Returns
            The end time in seconds
        """
        return self._end

    def start(self) -> float:
        """Retrieve the start time of the phoneme in seconds

        Returns
            The start time in seconds
        """
        return self._start
