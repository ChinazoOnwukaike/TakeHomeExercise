export interface BlockSummary {
  block_id: string;
  block_name: string;
  co2e_value: number;
  supplier_reported_co2e_value: number | null;
  active_co2e: number;
  source: "supplier-reported" | "industry-default";
}
