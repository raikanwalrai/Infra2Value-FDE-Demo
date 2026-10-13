import IncidentDashboard from "./IncidentDashboard"
import { useEffect, useMemo, useRef, useState } from "react"
import "./App.css"
import type {
  Metric,
  MetricLayer,
  Relationship,
  ValueGraph,
} from "./types/valueGraph"

const API_BASE_URL = "http://127.0.0.1:8000"

type ScenarioResult = {
  scenario_id: string
  scenario_name: string
  metric_results: {
    metric_id: string
    baseline_value: number
    scenario_value: number
    delta: number
  }[]
  baseline_annual_value: number
  scenario_annual_value: number
  annual_value_delta: number
}

function formatUsd(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value)
}

const layerLabels: Record<MetricLayer, string> = {
  infrastructure: "Infrastructure",
  technical_kpi: "Technical KPI",
  business_kpi: "Business KPI",
  financial_outcome: "Financial Outcome",
  cxo_outcome: "CXO Outcome",
}

const layerNumbers: Record<MetricLayer, string> = {
  infrastructure: "01",
  technical_kpi: "02",
  business_kpi: "03",
  financial_outcome: "04",
  cxo_outcome: "05",
}

function formatMetricValue(metric: Metric, value: number | null) {
  if (value === null) {
    return "-"
  }

  if (metric.unit === "%") {
    return `${value}%`
  }

  return `${value.toLocaleString()} ${metric.unit}`
}

function getMetric(graph: ValueGraph, id: string) {
  return graph.metrics.find((metric) => metric.id === id)
}

function getRelationship(
  graph: ValueGraph,
  sourceId: string,
  targetId: string,
): Relationship | undefined {
  return graph.relationships.find(
    (relationship) =>
      relationship.source_metric_id === sourceId &&
      relationship.target_metric_id === targetId,
  )
}

function CausalNode({
  metric,
}: {
  metric: Metric
}) {
  const isFinancial =
    metric.layer === "financial_outcome" ||
    metric.layer === "cxo_outcome"

  return (
    <article
      className={`causal-node ${
        isFinancial ? "causal-node-financial" : ""
      }`}
    >
      <div className="causal-node-header">
        <span className="causal-layer">
          {layerNumbers[metric.layer]} · {layerLabels[metric.layer]}
        </span>

        <span className="confidence-badge">
          {Math.round(metric.confidence * 100)}% confidence
        </span>
      </div>

      <h3>{metric.name}</h3>

      <p>{metric.description}</p>

      <div className="causal-values">
        <div>
          <span>Current</span>
          <strong>
            {formatMetricValue(metric, metric.current_value)}
          </strong>
        </div>

        <div className="value-arrow">→</div>

        <div>
          <span>Target</span>
          <strong>
            {formatMetricValue(metric, metric.target_value)}
          </strong>
        </div>
      </div>

      <div className="causal-source">
        Source: {metric.source.replaceAll("_", " ")}
      </div>
    </article>
  )
}

function RelationshipConnector({
  relationship,
}: {
  relationship: Relationship
}) {
  return (
    <div className="relationship-connector">
      <div className="connector-line" />

      <div className="relationship-label">
        <span>{relationship.relationship_type.replaceAll("_", " ")}</span>
        <small>
          coefficient: {relationship.coefficient.toLocaleString()}
        </small>
      </div>

      <div className="connector-arrow">↓</div>

      <div className="assumption">
        {relationship.assumption}
      </div>
    </div>
  )
}

function App() {
  const [graph, setGraph] = useState<ValueGraph | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [scenarioResult, setScenarioResult] =
    useState<ScenarioResult | null>(null)
  const [scenarioLoading, setScenarioLoading] = useState(false)
  const [scenarioError, setScenarioError] = useState<string | null>(null)
  const scenarioResultsRef = useRef<HTMLElement | null>(null)

  async function runScenario() {
    setScenarioLoading(true)
    setScenarioError(null)
    setScenarioResult(null)

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/value-graphs/starbucks/scenarios`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            scenario_id: "availability-demo",
            name: "Improve Network Availability",
            description:
              "Illustrative improvement from 99.5% to 99.9% availability.",
            overrides: [
              {
                metric_id: "network_availability",
                baseline_value: 99.5,
                scenario_value: 99.9,
              },
            ],
          }),
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : `Scenario request failed: ${response.status}`,
        )
      }

      setScenarioResult(data as ScenarioResult)
    } catch (err) {
      setScenarioError(
        err instanceof Error ? err.message : "Unable to run scenario.",
      )
    } finally {
      setScenarioLoading(false)
    }
  }

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/value-graphs/starbucks`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`API request failed: ${response.status}`)
        }

        return response.json()
      })
      .then((data: ValueGraph) => {
        setGraph(data)
        setError(null)
      })
      .catch((err: Error) => {
        setError(err.message)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  useEffect(() => {
    if (scenarioResult) {
      scenarioResultsRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      })
    }
  }, [scenarioResult])

  const causalPath = useMemo(() => {
    if (!graph) {
      return []
    }

    const path: Metric[] = []
    let currentId = "network_availability"

    const visited = new Set<string>()

    while (currentId && !visited.has(currentId)) {
      visited.add(currentId)

      const metric = getMetric(graph, currentId)

      if (!metric) {
        break
      }

      path.push(metric)

      const nextRelationship = graph.relationships.find(
        (relationship) =>
          relationship.source_metric_id === currentId &&
          !visited.has(relationship.target_metric_id),
      )

      if (!nextRelationship) {
        break
      }

      currentId = nextRelationship.target_metric_id
    }

    return path
  }, [graph])

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">I2V</div>

          <div>
            <div className="brand-name">Infra2Value</div>

            <div className="brand-tagline">
              Infrastructure-to-Business Value Intelligence
            </div>
          </div>
        </div>

        <nav className="nav">
          <a href="#value-map">Value Map</a>
          <a href="#scenarios">Scenarios</a>
          <a href="#cockpit">Executive Cockpit</a>
          <button className="ask-button">Ask Infra2Value</button>
        </nav>
      </header>

      <main>
        <section className="hero">
          <div className="hero-content">
            <div className="eyebrow">
              INFRASTRUCTURE → BUSINESS VALUE
            </div>

            <h1>
              Turn infrastructure metrics into measurable business outcomes.
            </h1>

            <p>
              Infra2Value connects infrastructure performance to business
              KPIs, financial impact and CXO outcomes through an explainable
              value graph.
            </p>

            <div className="hero-actions">
              <button
                className="primary-button"
                onClick={() =>
                  document.getElementById("causal-map")?.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                  })
                }
              >
                Explore Value Map
              </button>

              <button
                className="secondary-button"
                onClick={runScenario}
                disabled={scenarioLoading}
              >
                {scenarioLoading ? "Running Scenario..." : "Run a Scenario"}
              </button>
            </div>
          </div>

          <div className="value-chain">
            <div className="chain-title">VALUE CHAIN</div>

            <div className="chain">
              {(Object.keys(layerLabels) as MetricLayer[]).map(
                (layer, index) => (
                  <div key={layer} className="chain-node">
                    <span>
                      {String(index + 1).padStart(2, "0")}
                    </span>

                    {layerLabels[layer]}

                    {index < 4 && (
                      <div className="arrow">→</div>
                    )}
                  </div>
                ),
              )}
            </div>
          </div>
        </section>

        {scenarioResult && (
          <section ref={scenarioResultsRef} className="scenario-results" aria-live="polite">
            <div className="eyebrow">SCENARIO RESULTS</div>
            <h2>{scenarioResult.scenario_name}</h2>
            <p className="scenario-disclaimer">
              Illustrative demo only. Results depend on assumed relationships
              and coefficients; they are not verified customer outcomes.
            </p>

            <div className="scenario-result-grid">
              <article>
                <span>Baseline annual value</span>
                <strong>
                  {formatUsd(scenarioResult.baseline_annual_value)}
                </strong>
              </article>
              <article>
                <span>Scenario annual value</span>
                <strong>
                  {formatUsd(scenarioResult.scenario_annual_value)}
                </strong>
              </article>
              <article>
                <span>Annual value delta</span>
                <strong>
                  {formatUsd(scenarioResult.annual_value_delta)}
                </strong>
              </article>
            </div>

            <h3>Metric change</h3>
            {scenarioResult.metric_results.map((metric) => (
              <p key={metric.metric_id}>
                <strong>{metric.metric_id.replaceAll("_", " ")}</strong>:{" "}
                {metric.baseline_value}% → {metric.scenario_value}%{" "}
                (change: {metric.delta > 0 ? "+" : ""}{metric.delta.toFixed(1)}{" "}
                percentage points)
              </p>
            ))}
          </section>
        )}

        {scenarioError && (
          <p className="scenario-error" role="alert">
            Unable to run scenario: {scenarioError}
          </p>
        )}

        <IncidentDashboard />


        <section className="summary" id="cockpit">
          <div className="section-heading">
            <div>
              <div className="eyebrow">
                EXECUTIVE VALUE SNAPSHOT
              </div>


              <div className="customer-heading">
                {graph && (
                  <img
                    className="customer-logo"
                    src="/starbucks-logo.png"
                    alt="Starbucks logo"
                  />
                )}
                <div>
                  <h2>{graph ? "Starbucks" : "Loading Value Graph..."}</h2>
                  <p className="customer-subtitle">
                    Illustrative customer scenario · Value Graph
                  </p>
                </div>
              </div>
            </div>

            <span className="assumption-badge">
              API-driven data
            </span>
          </div>

          {loading && (
            <p className="metric-note">
              Loading value graph from Infra2Value API...
            </p>
          )}

          {error && (
            <p className="metric-note">
              Unable to load value graph: {error}
            </p>
          )}

          {graph && causalPath.length > 0 && (
            <div className="causal-map" id="causal-map">
              <div className="causal-map-intro">
                <div>
                  <div className="eyebrow">CAUSAL VALUE MAP</div>

                  <h2>
                    From infrastructure change to executive outcome
                  </h2>
                </div>

                <div className="map-summary">
                  <strong>{causalPath.length}</strong>
                  <span>metrics in impact path</span>
                </div>
              </div>

              <div className="causal-path">
                {causalPath.map((metric, index) => {
                  const nextMetric = causalPath[index + 1]

                  const relationship = nextMetric
                    ? getRelationship(
                        graph,
                        metric.id,
                        nextMetric.id,
                      )
                    : undefined

                  return (
                    <div key={metric.id}>
                      <CausalNode metric={metric} />

                      {relationship && (
                        <RelationshipConnector
                          relationship={relationship}
                        />
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </section>

        <section className="capabilities" id="value-map">
          <div className="section-heading">
            <div>
              <div className="eyebrow">CORE WORKSPACE</div>

              <h2>
                From metric change to business consequence
              </h2>
            </div>
          </div>

          {graph && (
            <div className="capability-grid">
              <article className="capability-card featured">
                <div className="card-number">01</div>

                <h3>Value Map</h3>

                <p>
                  Trace the causal path from infrastructure metrics
                  to financial and CXO outcomes.
                </p>

                <span>
                  {graph.metrics.length} metrics ·{" "}
                  {graph.relationships.length} relationships
                </span>
              </article>

              <article
                className="capability-card"
                id="scenarios"
              >
                <div className="card-number">02</div>

                <h3>Scenario Simulator</h3>

                <p>
                  Change infrastructure assumptions and immediately
                  see downstream value.
                </p>

                <span>
                  Ready for Value Engine
                </span>
              </article>

              <article className="capability-card">
                <div className="card-number">03</div>

                <h3>Ask Infra2Value</h3>

                <p>
                  Ask natural-language questions and receive
                  explainable, evidence-backed answers.
                </p>

                <span>
                  Graph-aware reasoning foundation
                </span>
              </article>
            </div>
          )}
        </section>
      </main>

      <footer>
        <span>Infra2Value MVP</span>

        <span>
          Infrastructure → Business → Financial → CXO
        </span>
      </footer>
    </div>
  )
}

export default App
