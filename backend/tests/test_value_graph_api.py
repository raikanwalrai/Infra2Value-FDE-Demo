from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_starbucks_value_graph():
    response = client.get(
        "/api/value-graphs/starbucks"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["customer_id"] == "starbucks"
    assert len(data["metrics"]) == 5
    assert len(data["relationships"]) == 4


def test_get_metric():
    response = client.get(
        "/api/value-graphs/starbucks/metrics/network_availability"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == "network_availability"
    assert data["name"] == "Network Availability"
    assert data["current_value"] == 99.5
    assert data["target_value"] == 99.9


def test_get_impact_path():
    response = client.get(
        "/api/value-graphs/starbucks/impact-path",
        params={
            "source_metric_id": "network_availability",
            "target_metric_id": "ceo_revenue_growth",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["customer_id"] == "starbucks"

    metric_ids = [
        metric["id"]
        for metric in data["metrics"]
    ]

    assert metric_ids == [
        "network_availability",
        "digital_transaction_recovery",
        "recovered_transactions",
        "incremental_revenue",
        "ceo_revenue_growth",
    ]

    assert len(data["relationships"]) == 4


def test_missing_customer():
    response = client.get(
        "/api/value-graphs/unknown_customer"
    )

    assert response.status_code == 404


def test_missing_metric():
    response = client.get(
        "/api/value-graphs/starbucks/metrics/does_not_exist"
    )

    assert response.status_code == 404


def test_missing_impact_path():
    response = client.get(
        "/api/value-graphs/starbucks/impact-path",
        params={
            "source_metric_id": "ceo_revenue_growth",
            "target_metric_id": "network_availability",
        },
    )

    assert response.status_code == 404
