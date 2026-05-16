import type { ComponentSummary, ComponentDetail } from "../types";
import { BASE } from "./client";

export const fetchComponents = async (): Promise<ComponentSummary[]> => {
  const res = await fetch(`${BASE}/api/components`);
  if (!res.ok) throw new Error("Failed to fetch components");
  return res.json();
};

export const fetchComponent = async (id: string): Promise<ComponentDetail> => {
  const res = await fetch(`${BASE}/api/components/${id}`);
  if (!res.ok) throw new Error("Failed to fetch component");
  return res.json();
};
