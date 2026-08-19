from django.test import Client


def test_readiness_only_allows_get(client: Client):
    assert client.get("/readiness").status_code == 200
    assert client.post("/readiness").status_code == 405
