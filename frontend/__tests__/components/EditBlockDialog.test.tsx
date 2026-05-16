import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import EditBlockDialog from "@/app/components/EditBlockDialog";
import { patchBlock } from "@/lib/api";
import type { BlockSummary } from "@/lib/types";

jest.mock("@/lib/api", () => ({
  patchBlock: jest.fn(),
}));

jest.mock("react-dom", () => ({
  ...jest.requireActual("react-dom"),
  createPortal: (node: React.ReactNode) => node,
}));

const mockPatchBlock = patchBlock as jest.MockedFunction<typeof patchBlock>;

const baseBlock: BlockSummary = {
  block_id: "block-123",
  block_name: "raw_production",
  co2e_value: 1.65,
  supplier_reported_co2e_value: 1.5,
  active_co2e: 1.5,
  source: "supplier-reported",
};

const defaultProps = {
  block: baseBlock,
  onSaved: jest.fn(),
  onClose: jest.fn(),
};

beforeEach(() => {
  jest.clearAllMocks();
});

describe("EditBlockDialog", () => {
  it("renders the block name", () => {
    render(<EditBlockDialog {...defaultProps} />);
    expect(screen.getByText("raw_production")).toBeInTheDocument();
  });

  it("renders the industry default value as read-only", () => {
    render(<EditBlockDialog {...defaultProps} />);
    expect(screen.getByText("1.65 kg CO₂e/unit")).toBeInTheDocument();
  });

  it("pre-fills the input with existing supplier value", () => {
    render(<EditBlockDialog {...defaultProps} />);
    expect(screen.getByRole("spinbutton")).toHaveValue(1.5);
  });

  it("leaves the input empty when no supplier value is set", () => {
    const block = { ...baseBlock, supplier_reported_co2e_value: null, source: "industry-default" as const };
    render(<EditBlockDialog {...defaultProps} block={block} />);
    expect(screen.getByRole("spinbutton")).toHaveValue(null);
  });

  it("calls patchBlock with the entered value on save", async () => {
    mockPatchBlock.mockResolvedValue({ block: baseBlock, total_footprint: 23.125 });
    const user = userEvent.setup();
    render(<EditBlockDialog {...defaultProps} />);

    await user.clear(screen.getByRole("spinbutton"));
    await user.type(screen.getByRole("spinbutton"), "1.20");
    await user.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => expect(mockPatchBlock).toHaveBeenCalledWith("block-123", 1.2));
  });

  it("calls patchBlock with null when input is cleared", async () => {
    mockPatchBlock.mockResolvedValue({ block: { ...baseBlock, supplier_reported_co2e_value: null, source: "industry-default" }, total_footprint: 26.25 });
    const user = userEvent.setup();
    render(<EditBlockDialog {...defaultProps} />);

    await user.clear(screen.getByRole("spinbutton"));
    await user.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => expect(mockPatchBlock).toHaveBeenCalledWith("block-123", null));
  });

  it("calls onSaved with updated block and footprint on success", async () => {
    const updatedBlock = { ...baseBlock, supplier_reported_co2e_value: 1.2, active_co2e: 1.2 };
    mockPatchBlock.mockResolvedValue({ block: updatedBlock, total_footprint: 23.0 });
    const user = userEvent.setup();
    render(<EditBlockDialog {...defaultProps} />);

    await user.clear(screen.getByRole("spinbutton"));
    await user.type(screen.getByRole("spinbutton"), "1.20");
    await user.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => expect(defaultProps.onSaved).toHaveBeenCalledWith(updatedBlock, 23.0));
  });

  it("shows an error message when the API fails", async () => {
    mockPatchBlock.mockRejectedValue(new Error("Network error"));
    const user = userEvent.setup();
    render(<EditBlockDialog {...defaultProps} />);

    await user.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => expect(screen.getByText("Save failed. Please try again.")).toBeInTheDocument());
  });

  it("disables the save button while saving", async () => {
    mockPatchBlock.mockReturnValue(new Promise(() => {}));
    const user = userEvent.setup();
    render(<EditBlockDialog {...defaultProps} />);

    await user.click(screen.getByRole("button", { name: "Save" }));

    expect(screen.getByRole("button", { name: "Saving…" })).toBeDisabled();
  });

  it("calls onClose when cancel is clicked", async () => {
    const user = userEvent.setup();
    render(<EditBlockDialog {...defaultProps} />);

    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(defaultProps.onClose).toHaveBeenCalled();
  });

  it("calls onClose when the backdrop is clicked", async () => {
    const user = userEvent.setup();
    const { container } = render(<EditBlockDialog {...defaultProps} />);

    const backdrop = container.firstChild as HTMLElement;
    await user.click(backdrop);

    expect(defaultProps.onClose).toHaveBeenCalled();
  });
});
