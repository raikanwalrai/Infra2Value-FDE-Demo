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



def test_run_scenario_success():
    response = client.post(
        "/api/value-graphs/starbucks/scenarios",
        json={
            "scenario_id": "availability-demo",
            "name": "Improve Network Availability",
            "description": "Illustrative scenario.",
            "overrides": [
                {
                    "metric_id": "network_availability",
                    "baseline_value": 99.5,
                    "scenario_value": 99.9,
                }
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["scenario_id"] == "availability-demo"
    assert data["baseline_annual_value"] == 0.0
    assert data["scenario_annual_value"] == 153600.0
    assert data["annual_value_delta"] == 153600.0
    assert data["metric_results"][0]["metric_id"] == "network_availability"


def test_run_scenario_unknown_metric():
    response = client.post(
        "/api/value-graphs/starbucks/scenarios",
        json={
            "scenario_id": "invalid-metric",
            "name": "Invalid Metric",
            "overrides": [
                {
                    "metric_id": "unknown_metric",
                    "baseline_value": 0.0,
                    "scenario_value": 1.0,
                }
            ],
        },
    )

    assert response.status_code == 422


def test_run_scenario_unknown_customer():
    response = client.post(
        "/api/value-graphs/unknown_customer/scenarios",
        json={
            "scenario_id": "unknown-customer",
            "name": "Unknown Customer",
            "overrides": [
                {
                    "metric_id": "network_availability",
                    "baseline_value": 99.5,
                    "scenario_value": 99.9,
                }
            ],
        },
    )

    assert response.status_code == 404
