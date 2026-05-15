"use client";

import { useState } from "react";
import { createPortal } from "react-dom";
import type { BlockSummary } from "@/lib/types";
import { patchBlock } from "@/lib/api";

interface Props {
  block: BlockSummary;
  onSaved: (updated: BlockSummary, newFootprint: number) => void;
  onClose: () => void;
}

const EditBlockDialog = ({ block, onSaved, onClose }: Props) => {
  const [value, setValue] = useState<string>(
    block.supplier_reported_co2e_value !== null
      ? String(block.supplier_reported_co2e_value)
      : "",
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const parsed = value.trim() === "" ? null : parseFloat(value);
      if (parsed !== null && isNaN(parsed)) {
        setError(
          "Enter a valid number or leave blank to use industry default.",
        );
        return;
      }
      const result = await patchBlock(block.block_id, parsed);
      onSaved(result.block, result.total_footprint);
    } catch {
      setError("Save failed. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <dialog
        open
        className="relative w-full max-w-md rounded-lg bg-white p-6 shadow-xl"
      >
        <h2 className="mb-1 text-lg font-semibold text-brand-dark">
          Edit block
        </h2>
        <p className="mb-4 text-sm text-brand-muted">{block.block_name}</p>

        <div className="mb-3 rounded-md bg-brand-surface px-4 py-3 text-sm">
          <span className="text-brand-muted">Industry default: </span>
          <span className="font-mono font-medium text-brand-dark">
            {block.co2e_value.toFixed(2)} kg CO₂e/unit
          </span>
        </div>

        <label className="block text-sm font-medium text-brand-dark mb-1">
          Supplier-reported value (kg CO₂e/unit)
        </label>
        <p className="text-xs text-brand-muted mb-2">
          Leave blank to fall back to the industry default.
        </p>
        <input
          type="number"
          step="0.01"
          min="0"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={`industry default: ${block.co2e_value.toFixed(2)}`}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-green"
        />

        {error && <p className="mt-2 text-xs text-red-600">{error}</p>}

        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="rounded-md border border-gray-200 px-4 py-2 text-sm text-brand-dark hover:bg-brand-surface"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="rounded-md bg-brand-dark px-4 py-2 text-sm text-white hover:opacity-90 disabled:opacity-50"
          >
            {saving ? "Saving…" : "Save"}
          </button>
        </div>
      </dialog>
    </div>,
    document.body,
  );
};

export default EditBlockDialog;
