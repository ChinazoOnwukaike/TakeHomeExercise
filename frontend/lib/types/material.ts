import type { BlockSummary } from "./block";

export interface MaterialDetail {
  material_id: string;
  material_name: string;
  weight: number;
  supplier_name: string | null;
  blocks: BlockSummary[];
}
