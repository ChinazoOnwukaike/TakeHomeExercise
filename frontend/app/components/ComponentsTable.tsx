"use client";

import React, { useState, useCallback } from "react";
import type {
  ComponentSummary,
  ComponentDetail,
  BlockSummary,
} from "@/lib/types";
import { fetchComponent } from "@/lib/api";
import MaterialRow from "./MaterialRow";

interface Props {
  components: ComponentSummary[];
}

const ComponentsTable = ({ components }: Props) => {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [details, setDetails] = useState<Record<string, ComponentDetail>>({});
  const [footprints, setFootprints] = useState<Record<string, number>>(() =>
    Object.fromEntries(
      components
        .filter((c) => c.total_footprint !== null)
        .map((c) => [c.component_id, c.total_footprint!]),
    ),
  );
  const [loading, setLoading] = useState<Set<string>>(new Set());
  const [search, setSearch] = useState("");

  const toggleExpand = async (id: string) => {
    if (expanded.has(id)) {
      setExpanded((prev) => {
        const s = new Set(prev);
        s.delete(id);
        return s;
      });
      return;
    }

    setExpanded((prev) => new Set([...prev, id]));

    if (!details[id]) {
      setLoading((prev) => new Set([...prev, id]));
      try {
        const detail = await fetchComponent(id);
        setDetails((prev) => ({ ...prev, [id]: detail }));
      } finally {
        setLoading((prev) => {
          const s = new Set(prev);
          s.delete(id);
          return s;
        });
      }
    }
  };

  const handleBlockUpdated = useCallback(
    (componentId: string) => (_updated: BlockSummary, newFootprint: number) => {
      setFootprints((prev) => ({ ...prev, [componentId]: newFootprint }));
    },
    [],
  );

  const filtered = components.filter((c) => {
    const term = search.toLowerCase().replace(/-/g, "");
    return (
      c.component_name.toLowerCase().includes(term) ||
      c.sku.toLowerCase().replace(/-/g, "").includes(term)
    );
  });

  return (
    <div>
      <div className="mb-4 flex justify-end">
        <input
          type="text"
          placeholder="Search components…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-72 rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-green"
        />
      </div>
      <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-brand-dark">
            <tr>
              <th className="pl-6 py-3.5 text-left font-semibold text-white w-[45%]">
                Component / Material / Block
              </th>
              <th className="py-3.5 text-right font-semibold text-white w-[10%]">
                Weight
              </th>
              <th className="py-3.5 text-right font-semibold text-white w-[15%]">
                CO₂e (kg)
              </th>
              <th className="py-3.5 text-center font-semibold text-white w-[15%]">
                Source
              </th>
              <th className="pr-6 py-3.5 w-[15%]" />
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {filtered.map((c) => {
              const isExpanded = expanded.has(c.component_id);
              const isLoading = loading.has(c.component_id);
              const detail = details[c.component_id];
              const displayFootprint = footprints[c.component_id];

              return (
                <React.Fragment key={c.component_id}>
                  <tr
                    className="cursor-pointer hover:bg-brand-surface"
                    onClick={() => toggleExpand(c.component_id)}
                  >
                    <td className="pl-6 py-3.5 font-semibold text-brand-dark">
                      <div className="flex items-center gap-2">
                        <span className="text-brand-green shrink-0">
                          {isExpanded ? "▾" : "▸"}
                        </span>
                        <span className="text-xs font-normal text-brand-muted shrink-0">
                          {c.sku}
                        </span>
                        <div>
                          {c.component_name}
                          {c.description && (
                            <p className="mt-0.5 text-xs font-normal text-brand-muted">
                              {c.description}
                            </p>
                          )}
                        </div>
                      </div>
                    </td>
                    <td />
                    <td className="py-3.5 text-right font-mono font-semibold text-brand-dark">
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
                          <td
                            colSpan={5}
                            className="pl-12 py-2 text-sm text-brand-muted italic"
                          >
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
    </div>
  );
};
export default ComponentsTable;
