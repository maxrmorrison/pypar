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


###############################################################################
# Utilities
###############################################################################


def path(file):
    """Resolve the file path of a test asset"""
    return Path(__file__).parent / 'assets' / file
