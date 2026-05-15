import type { ComponentSummary, ComponentDetail, BlockSummary } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000";

export async function fetchComponents(): Promise<ComponentSummary[]> {
  const res = await fetch(`${BASE}/api/components`);
  if (!res.ok) throw new Error("Failed to fetch components");
  return res.json();
}

export async function fetchComponent(id: string): Promise<ComponentDetail> {
  const res = await fetch(`${BASE}/api/components/${id}`);
  if (!res.ok) throw new Error("Failed to fetch component");
  return res.json();
}

export async function patchBlock(
  blockId: string,
  supplierReportedCo2e: number | null
): Promise<{ block: BlockSummary; total_footprint: number }> {
  const res = await fetch(`${BASE}/api/blocks/${blockId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ supplier_reported_co2e_value: supplierReportedCo2e }),
  });
  if (!res.ok) throw new Error("Failed to update block");
  return res.json();
}
