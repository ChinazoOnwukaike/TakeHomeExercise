import type { MaterialDetail } from "./material";

export interface ComponentSummary {
  component_id: string;
  sku: string;
  component_name: string;
  description: string | null;
  total_footprint: number | null;
}

export interface ComponentDetail extends ComponentSummary {
  materials: MaterialDetail[];
}
