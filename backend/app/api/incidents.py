
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from app.graph.value_graph_traversal import ValueGraphTraversal
from app.repositories.value_graph_repository import ValueGraphRepository

from app.models.incidents import Incident

router = APIRouter(prefix="/api/incidents", tags=["incidents"])
DATA_ROOT = Path(__file__).resolve().parents[3] / "data" / "incidents"


def load_incident(incident_id: str) -> Incident:
    for path in DATA_ROOT.glob("*.json"):
        try:
            data = json.loads(path.read_text())
            if data.get("id") == incident_id:
                return Incident.model_validate(data)
        except (json.JSONDecodeError, ValueError):
            continue

    raise HTTPException(
        status_code=404,
        detail=f"Incident not found: {incident_id}",
    )


@router.get("/{incident_id}")
def get_incident(incident_id: str):
    """Return an incident and its structured evidence."""
    return load_incident(incident_id).model_dump(mode="json")


@router.get("/{incident_id}/timeline")
def get_incident_timeline(incident_id: str):
    """Return incident evidence in chronological order."""
    incident = load_incident(incident_id)
    events = sorted(
        incident.evidence,
        key=lambda item: item.observed_at,
    )
    return {
        "incident_id": incident.id,
        "title": incident.title,
        "events": [
            event.model_dump(mode="json")
            for event in events
        ],
    }


@router.get("/{incident_id}/business-impact")
def get_incident_business_impact(incident_id: str):
    """Trace incident evidence to potential Value Graph outcomes.

    This endpoint exposes paths and assumptions. It does not attribute
    financial losses to an incident or calculate an incident-specific loss.
    """
    incident = load_incident(incident_id)

    value_repository = ValueGraphRepository(DATA_ROOT.parent)

    try:
        graph = value_repository.load(incident.customer_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Value graph not found for customer: {incident.customer_id}",
        )

    traversal = ValueGraphTraversal(graph)

    evidence_mappings = []
    source_metric_ids = set()

    for evidence in incident.evidence:
        mapped_metrics = []
        unmatched_metric_ids = []

        for metric_id in evidence.related_metric_ids:
            try:
                metric = traversal.get_metric(metric_id)
            except KeyError:
                unmatched_metric_ids.append(metric_id)
                continue

            source_metric_ids.add(metric_id)
            mapped_metrics.append({
                "id": metric.id,
                "name": metric.name,
                "layer": metric.layer,
                "unit": metric.unit,
                "current_value": metric.current_value,
                "target_value": metric.target_value,
                "source": metric.source,
                "confidence": metric.confidence,
            })

        evidence_mappings.append({
            "evidence_id": evidence.id,
            "evidence_title": evidence.title,
            "evidence_status": evidence.status,
            "evidence_source": evidence.source,
            "observed_at": evidence.observed_at.isoformat(),
            "mapped_metrics": mapped_metrics,
            "unmatched_metric_ids": unmatched_metric_ids,
        })

    outcome_metrics = [
        metric
        for metric in graph.metrics
        if metric.layer in ("financial_outcome", "cxo_outcome")
    ]

    impact_paths = []
    seen_paths = set()

    for source_metric_id in sorted(source_metric_ids):
        for target_metric in outcome_metrics:
            path = traversal.find_impact_path(
                source_metric_id,
                target_metric.id,
            )

            if not path:
                continue

            path_key = tuple(metric.id for metric in path)

            if path_key in seen_paths:
                continue

            seen_paths.add(path_key)

            relationships = traversal.get_relationships_for_path(path)

            impact_paths.append({
                "source_metric_id": source_metric_id,
                "target_metric_id": target_metric.id,
                "metrics": [
                    {
                        "id": metric.id,
                        "name": metric.name,
                        "layer": metric.layer,
                        "unit": metric.unit,
                        "current_value": metric.current_value,
                        "target_value": metric.target_value,
                        "source": metric.source,
                        "confidence": metric.confidence,
                    }
                    for metric in path
                ],
                "relationships": [
                    {
                        "source_metric_id": relationship.source_metric_id,
                        "target_metric_id": relationship.target_metric_id,
                        "relationship_type": relationship.relationship_type,
                        "coefficient": relationship.coefficient,
                        "confidence": relationship.confidence,
                        "assumption": relationship.assumption,
                    }
                    for relationship in relationships
                ],
                "interpretation": (
                    "Potential impact path based on model assumptions; "
                    "not confirmed incident causality."
                ),
            })

    return {
        "incident_id": incident.id,
        "customer_id": incident.customer_id,
        "analysis_status": "potential_impact_trace_only",
        "estimated_incident_loss": None,
        "financial_estimate_status": (
            "unavailable_without_calibrated_incident_impact"
        ),
        "explanation": (
            "The endpoint maps evidence to existing Value Graph metrics "
            "and returns potential downstream outcomes. It does not "
            "attribute financial loss to this incident."
        ),
        "evidence_mappings": evidence_mappings,
        "impact_paths": impact_paths,
    }
