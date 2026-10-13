
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

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
