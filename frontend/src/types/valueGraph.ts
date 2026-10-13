export type MetricLayer =
  | "infrastructure"
  | "technical_kpi"
  | "business_kpi"
  | "financial_outcome"
  | "cxo_outcome";

export interface Metric {
  id: string;
  name: string;
  description: string;
  domain: string;
  layer: MetricLayer;
  unit: string;
  current_value: number;
  target_value: number | null;
  source: string;
  confidence: number;
}

export interface Relationship {
  source_metric_id: string;
  target_metric_id: string;
  relationship_type:
    | "causes"
    | "influences"
    | "enables"
    | "contributes_to";
  coefficient: number;
  confidence: number;
  assumption: string;
}

export interface ValueGraph {
  customer_id: string;
  metrics: Metric[];
  relationships: Relationship[];
}
