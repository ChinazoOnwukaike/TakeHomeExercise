"use client";

import { useState } from "react";
import type { BlockSummary } from "@/lib/types";
import EditBlockDialog from "./EditBlockDialog";

interface Props {
  block: BlockSummary;
  onBlockUpdated: (updated: BlockSummary, newFootprint: number) => void;
}

export default function BlockRow({ block, onBlockUpdated }: Props) {
  const [editing, setEditing] = useState(false);
  const [current, setCurrent] = useState(block);

  function handleSaved(updated: BlockSummary, newFootprint: number) {
    setCurrent(updated);
    setEditing(false);
    onBlockUpdated(updated, newFootprint);
  }

  return (
    <>
      <tr className="bg-brand-surface border-t border-gray-100">
        <td className="pl-24 py-2 text-sm text-brand-dark">{current.block_name}</td>
        <td className="py-2 text-sm text-right font-mono text-brand-dark">
          {current.active_co2e.toFixed(2)}
        </td>
        <td className="py-2 text-sm text-center">
          <span
            className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
              current.source === "supplier-reported"
                ? "bg-brand-green/20 text-brand-dark"
                : "bg-gray-200 text-brand-muted"
            }`}
          >
            {current.source}
          </span>
        </td>
        <td className="py-2 pr-4 text-right">
          <button
            onClick={() => setEditing(true)}
            className="text-xs text-brand-green font-medium hover:underline"
          >
            Edit
          </button>
        </td>
      </tr>

      {editing && (
        <EditBlockDialog
          block={current}
          onSaved={handleSaved}
          onClose={() => setEditing(false)}
        />
      )}
    </>
  );
}
