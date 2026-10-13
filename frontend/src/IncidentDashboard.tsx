
import { useEffect, useState } from "react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react"
import "@xyflow/react/dist/style.css"
import "./IncidentDashboard.css"

const API_BASE_URL = "http://127.0.0.1:8000"
const INCIDENT_ID = "INC-2026-001"

type Evidence = {
  id: string
  kind: "metric" | "log" | "event" | "transaction"
  source: string
  observed_at: string
  title: string
  description: string
  status: "observed" | "inferred"
  metric_name?: string | null
  value?: number | null
  unit?: string | null
  confidence: number
  related_metric_ids: string[]
}

type Incident = {
  id: string
  customer_id: string
  title: string
  summary: string
  severity: string
  status: string
  started_at: string
  evidence: Evidence[]
}

const nodes: Node[] = [
  {
    id: "incident",
    position: { x: 30, y: 130 },
    data: { label: "Payment degradation" },
    style: { background: "#fff0e8", border: "1px solid #e9a078", width: 190 },
  },
  {
    id: "latency",
    position: { x: 290, y: 30 },
    data: { label: "Network latency" },
    style: { background: "#eaf2ff", border: "1px solid #8baee8", width: 170 },
  },
  {
    id: "errors",
    position: { x: 290, y: 150 },
    data: { label: "Payment error rate" },
    style: { background: "#eaf2ff", border: "1px solid #8baee8", width: 170 },
  },
  {
    id: "outcome",
    position: { x: 290, y: 270 },
    data: { label: "Successful payments" },
    style: { background: "#eaf8ef", border: "1px solid #86c69c", width: 170 },
  },
  {
    id: "hypothesis",
    position: { x: 550, y: 130 },
    data: { label: "Possible network contribution (hypothesis)" },
    style: {
      background: "#fff8dc",
      border: "1px dashed #c8a94b",
      width: 220,
    },
  },
]

const edges: Edge[] = [
  { id: "e1", source: "incident", target: "latency", label: "observed signal" },
  { id: "e2", source: "incident", target: "errors", label: "observed signal" },
  { id: "e3", source: "incident", target: "outcome", label: "observed signal" },
  {
    id: "e4",
    source: "latency",
    target: "hypothesis",
    label: "inferred · 55% confidence",
    animated: true,
    style: { stroke: "#c8a94b", strokeDasharray: "5 5" },
  },
  {
    id: "e5",
    source: "errors",
    target: "hypothesis",
    label: "investigate",
    style: { stroke: "#c8a94b", strokeDasharray: "5 5" },
  },
]

function formatTime(value: string) {
  return new Date(value).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  }) + " UTC"
}

export default function IncidentDashboard() {
  const [incident, setIncident] = useState<Incident | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/incidents/${INCIDENT_ID}`)
      .then((response) => {
        if (!response.ok) throw new Error(`API returned ${response.status}`)
        return response.json()
      })
      .then((data: Incident) => setIncident(data))
      .catch((err: Error) => setError(err.message))
  }, [])

  if (error) {
    return (
      <section className="incident-dashboard">
        <h2>Incident investigation</h2>
        <p role="alert">Unable to load incident: {error}</p>
        <p>Check that the Infra2Value API is running on port 8000.</p>
      </section>
    )
  }

  if (!incident) {
    return (
      <section className="incident-dashboard">
        <p>Loading incident evidence...</p>
      </section>
    )
  }

  const evidence = [...incident.evidence].sort(
    (a, b) =>
      new Date(a.observed_at).getTime() -
      new Date(b.observed_at).getTime(),
  )

  const latency = evidence.find((item) => item.metric_name === "network_latency")
  const errorRate = evidence.find((item) => item.metric_name === "payment_error_rate")
  const successfulPayments = evidence.find(
    (item) => item.metric_name === "successful_payments",
  )

  const percentageData = [
    errorRate && {
      signal: "Payment errors",
      value: errorRate.value ?? 0,
    },
    successfulPayments && {
      signal: "Successful payments",
      value: successfulPayments.value ?? 0,
    },
  ].filter((item): item is { signal: string; value: number } => Boolean(item))

  return (
    <section className="incident-dashboard" id="incidents">
      <div className="incident-heading">
        <div>
          <div className="eyebrow">INCIDENT INTELLIGENCE</div>
          <h2>{incident.title}</h2>
          <p>{incident.id} · Started {formatTime(incident.started_at)}</p>
        </div>
        <div className="incident-badges">
          <span className="severity-badge">{incident.severity}</span>
          <span className="status-badge">{incident.status}</span>
        </div>
      </div>

      <p className="incident-disclaimer">
        Synthetic demonstration data only. These observations are illustrative,
        not live customer telemetry. The suspected relationship is a hypothesis,
        not a confirmed root cause.
      </p>

      <div className="incident-kpis">
        <article className="incident-kpi">
          <span>Network latency</span>
          <strong>
            {latency?.value ?? "—"} {latency?.unit ?? ""}
          </strong>
          <small>Observed signal</small>
        </article>
        <article className="incident-kpi">
          <span>Payment error rate</span>
          <strong>
            {errorRate?.value ?? "—"}{errorRate?.unit ?? ""}
          </strong>
          <small>Observed signal</small>
        </article>
        <article className="incident-kpi">
          <span>Successful payments</span>
          <strong>
            {successfulPayments?.value ?? "—"}{successfulPayments?.unit ?? ""}
          </strong>
          <small>Relative to baseline</small>
        </article>
        <article className="incident-kpi">
          <span>Evidence items</span>
          <strong>{evidence.length}</strong>
          <small>
            {evidence.filter((item) => item.status === "inferred").length} inferred
          </small>
        </article>
      </div>

      <div className="incident-visual-grid">
        <article className="incident-panel">
          <h3>Observed payment signals</h3>
          <p className="panel-note">
            Separate observations, not a time-series trend.
          </p>
          <div className="incident-chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={percentageData} margin={{ top: 12, right: 12, bottom: 8, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="signal" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} unit="%" />
                <Tooltip formatter={(value) => [`${value}%`, "Observed value"]} />
                <Bar dataKey="value" fill="#4267a9" radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="incident-panel">
          <h3>Evidence timeline</h3>
          <p className="panel-note">Ordered by observation time · UTC</p>
          <ol className="evidence-timeline">
            {evidence.map((item) => (
              <li key={item.id} className={item.status === "inferred" ? "inferred" : ""}>
                <div className="timeline-time">{formatTime(item.observed_at)}</div>
                <div className="timeline-content">
                  <strong>{item.title}</strong>
                  <span>{item.description || item.source}</span>
                  <small>
                    {item.id} · {item.status}
                    {item.status === "inferred"
                      ? ` · ${(item.confidence * 100).toFixed(0)}% confidence`
                      : ""}
                  </small>
                </div>
              </li>
            ))}
          </ol>
        </article>
      </div>

      <article className="incident-panel evidence-graph-panel">
        <h3>Evidence relationship graph</h3>
        <p className="panel-note">
          Drag nodes to explore. Dashed amber links represent hypotheses, not proven causality.
        </p>
        <div className="evidence-graph">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            fitView
            fitViewOptions={{ padding: 0.2 }}
            nodesDraggable
            elementsSelectable
          >
            <Background />
            <MiniMap />
            <Controls />
          </ReactFlow>
        </div>
      </article>
    </section>
  )
}
