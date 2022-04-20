from packages.Sipuni.Client import Client
from packages.Sipuni.services import CallStatisticService


def test_sipuni_client():
    client = Client('test', 'test')
    assert type(client.calls_stats) == CallStatisticService
