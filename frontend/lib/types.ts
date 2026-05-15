export interface BlockSummary {
  block_id: string;
  block_name: string;
  co2e_value: number;
  supplier_reported_co2e_value: number | null;
  active_co2e: number;
  source: "supplier-reported" | "industry-default";
}

export interface MaterialDetail {
  material_id: string;
  material_name: string;
  weight: number;
  supplier_name: string | null;
  blocks: BlockSummary[];
}

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
