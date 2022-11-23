import pytest
from pathlib import Path
import json


@pytest.fixture(scope="session")
def lead_example():
    file = json.load(open(Path(__file__).resolve().parent / "lead.json"))
    return file
