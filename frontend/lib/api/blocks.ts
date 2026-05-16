import type { BlockSummary } from "../types";
import { BASE } from "./client";

export const patchBlock = async (
  blockId: string,
  supplierReportedCo2e: number | null,
): Promise<{ block: BlockSummary; total_footprint: number }> => {
  const res = await fetch(`${BASE}/api/blocks/${blockId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      supplier_reported_co2e_value: supplierReportedCo2e,
    }),
  });
  if (!res.ok) throw new Error("Failed to update block");
  return res.json();
};
