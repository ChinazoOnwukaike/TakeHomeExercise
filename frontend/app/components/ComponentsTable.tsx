"use client";

import React, { useState, useCallback } from "react";
import type { ComponentSummary, ComponentDetail, BlockSummary } from "@/lib/types";
import { fetchComponent } from "@/lib/api";
import MaterialRow from "./MaterialRow";

interface Props {
  components: ComponentSummary[];
}

export default function ComponentsTable({ components }: Props) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [details, setDetails] = useState<Record<string, ComponentDetail>>({});
  const [footprints, setFootprints] = useState<Record<string, number>>(() =>
    Object.fromEntries(
      components.filter((c) => c.total_footprint !== null).map((c) => [c.component_id, c.total_footprint!])
    )
  );
  const [loading, setLoading] = useState<Set<string>>(new Set());

  async function toggleExpand(id: string) {
    if (expanded.has(id)) {
      setExpanded((prev) => { const s = new Set(prev); s.delete(id); return s; });
      return;
    }

    setExpanded((prev) => new Set([...prev, id]));

    if (!details[id]) {
      setLoading((prev) => new Set([...prev, id]));
      try {
        const detail = await fetchComponent(id);
        setDetails((prev) => ({ ...prev, [id]: detail }));
      } finally {
        setLoading((prev) => { const s = new Set(prev); s.delete(id); return s; });
      }
    }
  }

  const handleBlockUpdated = useCallback(
    (componentId: string) => (_updated: BlockSummary, newFootprint: number) => {
      setFootprints((prev) => ({ ...prev, [componentId]: newFootprint }));
    },
    []
  );

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="pl-4 py-3 text-left font-semibold text-gray-700 w-1/2">
              Component / Material / Block
            </th>
            <th className="py-3 text-right font-semibold text-gray-700 w-1/6">
              Weight / CO₂e value
            </th>
            <th className="py-3 text-center font-semibold text-gray-700 w-1/6">Source</th>
            <th className="pr-4 py-3 w-1/6" />
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-100">
          {components.map((c) => {
            const isExpanded = expanded.has(c.component_id);
            const isLoading = loading.has(c.component_id);
            const detail = details[c.component_id];
            const displayFootprint = footprints[c.component_id];

            return (
              <React.Fragment key={c.component_id}>
                <tr
                  className="cursor-pointer hover:bg-blue-50/60"
                  onClick={() => toggleExpand(c.component_id)}
                >
                  <td className="pl-4 py-3 font-semibold text-gray-900">
                    <span className="mr-2 text-gray-400">{isExpanded ? "▾" : "▸"}</span>
                    {c.component_name}
                    <span className="ml-2 text-xs font-normal text-gray-400">{c.sku}</span>
                  </td>
                  <td className="py-3 text-right font-mono font-semibold text-gray-900">
                    {displayFootprint !== undefined
                      ? `${displayFootprint.toFixed(3)} kg CO₂e`
                      : "—"}
                  </td>
                  <td />
                  <td />
                </tr>

                {isExpanded && (
                  <>
                    {isLoading && (
                      <tr key={`${c.component_id}-loading`}>
                        <td colSpan={4} className="pl-12 py-2 text-sm text-gray-400 italic">
                          Loading…
                        </td>
                      </tr>
                    )}
                    {detail &&
                      detail.materials.map((mat) => (
                        <MaterialRow
                          key={mat.material_id}
                          material={mat}
                          onBlockUpdated={handleBlockUpdated(c.component_id)}
                        />
                      ))}
                  </>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
