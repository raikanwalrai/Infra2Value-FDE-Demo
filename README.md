# Infra2Value
### Infrastructure-to-Business Value Intelligence

Infra2Value is an engineering MVP that demonstrates how infrastructure
metrics can be connected to technical KPIs, business outcomes, financial
impact and executive-level value.

The central idea is simple:

Infrastructure Metric
    -> Technical KPI
    -> Business KPI
    -> Financial Outcome
    -> CXO Outcome

Rather than stopping at infrastructure health, the platform models a
causal value chain and calculates the potential business impact of a
change in an infrastructure metric.

## Why Infra2Value?

Infrastructure investments are often justified using availability,
capacity, reliability and operational-efficiency measures. Business
leaders need to understand how those measures may influence transactions,
revenue and strategic outcomes.

Infra2Value provides a structured way to represent these relationships,
make assumptions explicit and calculate scenario-based outcomes.

## Current MVP Capabilities

- JSON-based value graphs representing metrics and causal relationships.
- A FastAPI backend for retrieving value graphs, metrics and impact paths.
- A deterministic Python value engine for impact calculations.
- Scenario mappings and graph-based propagation of potential outcomes.
- A React and TypeScript frontend for exploring the value graph.
- Automated backend tests covering graph models, traversal, APIs,
  calculations and scenario propagation.

The numerical engine is deterministic: given the same inputs and
assumptions, it should produce the same calculated result.

## Architecture

| Layer | Current implementation |
|---|---|
| User interface | React, TypeScript and Vite |
| API | Python and FastAPI |
| Domain model | JSON value graph |
| Impact calculations | Python value engine |
| Scenario analysis | Scenario mappings and propagation |
| Quality | Pytest and frontend production build |

LLM-based agents, an LLM gateway, richer interactive graph visualisation,
and hosted deployment are potential extensions. They should not be
considered implemented capabilities unless explicitly demonstrated in
the current code.

## Example: Infrastructure to Revenue

The included Starbucks-labelled dataset illustrates a hypothetical
digital-transaction value chain:

1. Network availability improves from an assumed 99.5% to 99.9%.
2. A scenario assumes that 40% of otherwise failed digital transactions
   can be recovered.
3. The model uses an assumed opportunity of 4,000 transactions per month.
4. An assumed average transaction value of USD 8 is used to estimate
   potential incremental revenue.
5. Monthly revenue is annualised to illustrate an executive-level outcome.

**Important:** This dataset is illustrative. Its values and causal
relationships are assumptions for demonstrating the model, not verified
Starbucks operational data, forecasts or business results. Actual outcomes
would require validated customer data and agreement on the assumptions.

## Run Locally

Requirements:
- Python 3.12 or a compatible version supported by the dependencies.
- Node.js and npm.

### 1. Start the backend

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
PYTHONPATH=backend uvicorn app.main:app --reload
```

The API should be available at `http://127.0.0.1:8000`.
The health endpoint is `http://127.0.0.1:8000/health`.

### 2. Start the frontend

In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite.

### 3. Run backend tests

From the repository root, with the Python environment activated:

```bash
PYTHONPATH=backend python -m pytest -q
```

### 4. Build the frontend

```bash
cd frontend
npm ci
npm run build
```

## Project Principles

- **Value Graph:** represents domain knowledge and causal relationships.
- **Value Engine:** owns numerical calculations.
- **Explicit assumptions:** separates illustrative inputs from validated data.
- **API-first design:** exposes value graph functionality through FastAPI.
- **Reproducibility:** supports automated tests for core behaviour.

## Roadmap

Potential next steps include:

- An agentic investigation workflow using controlled, auditable tools.
- Mock enterprise connectors for network, cloud/datacentre, collaboration
  and security telemetry.
- Evidence-linked incident diagnosis and hypothesis generation.
- A policy gate for read-only tool execution.
- An executive view linking technical findings to business impact.
- Continuous integration and a reproducible deployment pipeline.

These items are roadmap ideas, not claims about current functionality.

## Status

An evolving MVP. Interfaces, capabilities and architecture may change as
the product develops.
