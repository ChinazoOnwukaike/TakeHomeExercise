"use client";

import { useState } from "react";
import type { MaterialDetail, BlockSummary } from "@/lib/types";
import BlockRow from "./BlockRow";

interface Props {
  material: MaterialDetail;
  onBlockUpdated: (updated: BlockSummary, newFootprint: number) => void;
}

const MaterialRow = ({ material, onBlockUpdated }: Props) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      <tr
        className="border-t border-gray-100 cursor-pointer hover:bg-brand-surface"
        onClick={() => setExpanded((v) => !v)}
      >
        <td className="pl-12 py-2.5 text-sm font-medium text-brand-dark">
          <span className="mr-1.5 text-brand-green">{expanded ? "▾" : "▸"}</span>
          {material.material_name}
          {material.supplier_name && (
            <span className="ml-2 text-xs text-brand-muted">({material.supplier_name})</span>
          )}
        </td>
        <td className="py-2.5 text-sm text-right font-mono text-brand-muted">
          {material.weight.toFixed(2)} kg
        </td>
        <td />
        <td />
        <td />
      </tr>

      {expanded &&
        material.blocks.map((block) => (
          <BlockRow
            key={block.block_id}
            block={block}
            onBlockUpdated={onBlockUpdated}
          />
        ))}
    </>
  );
};

export default MaterialRow;
