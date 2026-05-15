import type { ComponentSummary, ComponentDetail } from "../types";
import { BASE } from "./client";

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
