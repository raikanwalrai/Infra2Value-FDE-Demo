import { useEffect, useState } from "react"
import "./BusinessImpactTrace.css"

const API = "http://127.0.0.1:8000"
const INCIDENT = "INC-2026-001"

type Metric = {
  id: string
  name: string
  layer: string
  unit: string
  current_value: number
  target_value?: number
  confidence: number
}

type Relationship = {
  source_metric_id: string
  target_metric_id: string
  relationship_type: string
  confidence: number
  assumption: string
}

type ImpactPath = {
  source_metric_id: string
  target_metric_id: string
  metrics: Metric[]
  relationships: Relationship[]
  interpretation: string
}

type ImpactData = {
  explanation: string
  estimated_incident_loss: number | null
  evidence_mappings: Array<{ evidence_id: string }>
  impact_paths: ImpactPath[]
}

export default function BusinessImpactTrace() {
  const [data, setData] = useState<ImpactData | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    fetch(`${API}/api/incidents/${INCIDENT}/business-impact`)
      .then((response) => {
        if (!response.ok) throw new Error(`API returned ${response.status}`)
        return response.json()
      })
      .then((result: ImpactData) => setData(result))
      .catch((err: Error) => setError(err.message))
  }, [])

  if (error) {
    return <article className="incident-panel"><h3>Business impact trace</h3><p role="alert">{error}</p></article>
  }

  if (!data) {
    return <article className="incident-panel"><h3>Business impact trace</h3><p>Loading impact trace...</p></article>
  }

  const primaryPath =
    data.impact_paths.find(
      (path) =>
        path.source_metric_id === "network_availability" &&
        path.target_metric_id === "ceo_revenue_growth",
    ) ??
    data.impact_paths.find(
      (path) => path.metrics[path.metrics.length - 1]?.layer === "cxo_outcome",
    )

  const paths = primaryPath ? [primaryPath] : []

  return (
    <article className="incident-panel business-impact-panel">
      <h3>Business impact trace</h3>
      <p className="panel-note">
        Potential paths from incident evidence to executive outcomes.
      </p>

      <div className="impact-warning">
        <strong>Incident-specific financial loss: not calculated</strong>
        <p>{data.explanation}</p>
      </div>

      <div className="impact-evidence-summary">
        <strong>{data.evidence_mappings.length} evidence items assessed</strong>
        <p>Observed signals and inferred relationships are mapped to the customer Value Graph. The trace below is a modelled path, not proof of causality.</p>
      </div>

      <div className="impact-path-list">
        {paths.map((path) => (
          <section className="impact-path" key={path.source_metric_id}>
            <p>Trace from <code>{path.source_metric_id}</code></p>
            <div className="impact-chain">
              {path.metrics.map((metric, index) => (
                <div className="impact-step" key={metric.id}>
                  <div className="impact-node">
                    <small>{metric.layer.replaceAll("_", " ")}</small>
                    <strong>{metric.name}</strong>
                    <small>Current: {metric.current_value} {metric.unit}</small>
                    <small>Model target: {metric.target_value ?? "—"} {metric.unit}</small>
                    <small>Metric confidence: {(metric.confidence * 100).toFixed(0)}%</small>
                  </div>
                  {index < path.metrics.length - 1 && (
                    <span className="impact-arrow" aria-hidden="true">→</span>
                  )}
                </div>
              ))}
            </div>

            <h4>Relationship assumptions</h4>
            {path.relationships.map((item) => (
              <div className="impact-assumption" key={`${item.source_metric_id}-${item.target_metric_id}`}>
                <strong>{item.source_metric_id} → {item.target_metric_id}</strong>
                <small>{item.relationship_type} · Confidence {(item.confidence * 100).toFixed(0)}%</small>
                <p>{item.assumption}</p>
              </div>
            ))}
            <p className="impact-footnote">{path.interpretation}</p>
          </section>
        ))}
      </div>

      <p className="impact-footnote">
        Synthetic demonstration data. Modelled relationships do not prove root
        cause or realised financial benefit.
      </p>
    </article>
  )
}
