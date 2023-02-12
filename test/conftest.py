from pathlib import Path

import pytest

import pypar


###############################################################################
# Test fixtures
###############################################################################


@pytest.fixture(scope='session')
def alignment():
    """Retrieve the alignment to use for testing"""
    return pypar.Alignment(path('test.json'))

@pytest.fixture(scope='session')
def text():
    """Retrieve the speech transcript"""
    with open(path('test.txt')) as file:
        return file.read()


@pytest.fixture(scope='session')
def textgrid():
    """Retrieve the speech textgrid"""
    return pypar.Alignment(path('test.TextGrid'))


@pytest.fixture(scope='session')
def float_alignment():
    """Retrieve special alignment for float testing"""
    return pypar.Alignment(path('float.json'))


###############################################################################
# Utilities
###############################################################################


def path(file):
    """Resolve the file path of a test asset"""
    return Path(__file__).parent / 'assets' / file
