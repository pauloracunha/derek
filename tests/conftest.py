import pytest

from pipeline.s03_extract_acts import run


@pytest.fixture(scope="session")
def places():
    return run()
