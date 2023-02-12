import tempfile
from pathlib import Path

import pypar


###############################################################################
# Test alignment
###############################################################################


def test_find(alignment):
    """Test finding words in the alignment"""
    assert alignment.find('the mouse') == 7
    assert alignment.find('the dog') == -1


def test_phoneme_at_time(alignment):
    """Test queries for current phoneme given a time in seconds"""
    assert alignment.phoneme_at_time(-1.) is None
    assert str(alignment.phoneme_at_time(1.5)) == pypar.SILENCE
    assert str(alignment.phoneme_at_time(1.9)) == 'AH0'
    assert str(alignment.phoneme_at_time(4.5)) == 'S'
    assert alignment.phoneme_at_time(6.) is None


def test_phoneme_bounds(alignment):
    """Test frame boundaries of phonemes"""
    bounds = alignment.phoneme_bounds(10000, 100)
    assert bounds[0] == (27, 44)
    assert bounds[4] == (75, 86)


def test_load(textgrid):
    """Test textgrid loading"""
    pass


def test_save(alignment):
    """Test saving and reloading alignment"""
    with tempfile.TemporaryDirectory() as directory:
        # Test json
        file = Path(directory) / 'alignment.json'
        alignment.save(file)
        assert alignment == pypar.Alignment(file)

        # Test textgrid
        file = Path(directory) / 'alignment.TextGrid'
        alignment.save(file)
        assert alignment == pypar.Alignment(file)


def test_string(text, alignment):
    """Test the alignment string representation"""
    text = text.replace('"', '')
    text = text.replace('?', '')
    text = text.replace(',', '')
    assert text.upper() == str(alignment)


def test_word_at_time(alignment):
    """Test queries for current word given a time in seconds"""
    assert alignment.word_at_time(-1.) is None
    assert str(alignment.word_at_time(1.)) == 'PARDON'
    assert str(alignment.word_at_time(4.1)) == 'DID'
    assert alignment.word_at_time(6.) is None


def test_word_bounds(alignment):
    """Test frame boundaries of words"""
    bounds = alignment.word_bounds(10000, 100)
    assert bounds[0] == (27, 44)
    assert bounds[3] == (93, 149)


def test_float_update(float_alignment):
    for i in range(1, len(float_alignment)):
        assert float_alignment[i].start() >= float_alignment[i-1].end()
    float_alignment.update(start=0.)
    for i in range(1, len(float_alignment)):
        assert float_alignment[i].start() >= float_alignment[i-1].end()
