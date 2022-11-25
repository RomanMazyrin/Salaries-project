from amocrm_components.ApiIterator import BaseApiIterator
import pytest


class MockApiIterator(BaseApiIterator):
    def __init__(self, mock_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock_data = mock_data

    def _request(self, request_params):
        return self.mock_data


@pytest.fixture
def leads_data():
    return [1, 2, 3, 4, 5]


def test_api_iterator(leads_data):
    a = MockApiIterator(leads_data, url="")
    res = []
    for lead in a.get_next():
        res.append(lead)
    assert len(res) == 5
