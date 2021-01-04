import copy

import pypar


###############################################################################
# Test alignment comparisons
###############################################################################


def test_per_frame_rate(alignment):
    """Test the per-frame speed difference between alignments"""
    stretch_and_assert(alignment, .5)
    stretch_and_assert(alignment, 1.)
    stretch_and_assert(alignment, 2.)


###############################################################################
# Utilities
###############################################################################


def stretch(alignment, factor):
    """Time-stretch the alignment by a constant factor"""
    # Get phoneme durations
    durations = [factor * p.duration() for p in alignment.phonemes()]
    alignment = copy.deepcopy(alignment)
    alignment.update(durations=durations)
    return alignment


def stretch_and_assert(alignment, factor, sample_rate=10000, hopsize=100):
    """Time-stretch and perform test assertions"""
    # Get per-frame rate differences
    result = pypar.compare.per_frame_rate(alignment,
                                          stretch(alignment, factor),
                                          sample_rate,
                                          hopsize)

    # Perform assertions
    assert len(result) == 1 + int(alignment.duration() * sample_rate / hopsize)
    for item in result:
        assert item == factor
