import numpy as np


###############################################################################
# Alignment comparisons
###############################################################################


def per_frame_rate(alignment_a, alignment_b, sample_rate, hopsize):
    """Compute the per-frame rate difference between alignments A and B

    Arguments
        alignment_a : Alignment
            The source alignment
        alignment_b : Alignment
            The target alignment
        sample_rate : int
            The audio sampling rate
        hopsize : int
            The number of samples between successive frames

    Returns
        rates : list[float]
            The frame-wise relative speed of alignment B to alignment A
    """
    # Create dict mapping phoneme to relative rate
    rates_per_phoneme = per_phoneme_rate(alignment_a, alignment_b)
    dict_keys = [phoneme_tuple(phoneme) for phoneme in alignment_a.phonemes()]
    rate_map = dict(zip(dict_keys, rates_per_phoneme))

    # Query the dict every hopsize seconds
    frames = 1 + int(alignment_a.end() * sample_rate / hopsize)
    return [rate_map[phoneme_tuple(alignment_a.phoneme_at_time(t))]
            for t in np.linspace(0., alignment_a.end(), frames)]


def per_phoneme_rate(alignment_a, alignment_b):
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


###############################################################################
# Alignment comparisons
###############################################################################


def phoneme_tuple(phoneme):
    """Convert phoneme to hashable tuple representation

    Arguments
        phoneme - The phoneme to convert

    Returns
        tuple(float, float, string)
            The phoneme represented as a tuple
    """
    return (phoneme.start(), phoneme.end(), str(phoneme))
