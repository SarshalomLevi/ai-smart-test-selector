import pytest


@pytest.mark.integration
def test_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "message" in res.json()


@pytest.mark.integration
def test_rank_tests(client):
    res = client.get("/rank-tests")
    assert res.status_code == 200

    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.integration
def test_available_tests(client):
    res = client.get("/available-tests")
    assert res.status_code == 200

    data = res.json()
    assert "tests" in data
    assert isinstance(data["tests"], list)


@pytest.mark.integration
def test_top_risky(client):
    res = client.get("/top-risky")
    assert res.status_code == 200

    data = res.json()
    assert isinstance(data, list)


@pytest.mark.integration
def test_simulate_test(client):
    tests = client.get("/available-tests").json()["tests"]
    test_name = tests[0]

    res = client.get(f"/simulate-test/{test_name}")
    assert res.status_code == 200

    data = res.json()
    assert "risk" in data
    assert "result" in data
