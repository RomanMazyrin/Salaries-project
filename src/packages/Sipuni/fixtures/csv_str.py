import pytest
from pathlib import Path


@pytest.fixture(scope='session')
def calls_csv_str():
    file = open(Path(__file__).resolve().parent / "calls.csv")
    try:
        yield file.read()
    finally:
        file.close()
