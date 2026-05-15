import { fetchComponents } from "@/lib/api";
import ComponentsTable from "./components/ComponentsTable";

export const dynamic = "force-dynamic";

export default async function Page() {
  let components;
  try {
    components = await fetchComponents();
  } catch {
    return (
      <main className="max-w-5xl mx-auto px-4 py-12">
        <p className="text-red-600">
          Could not connect to the backend. Make sure the Flask server is running on port 5000.
        </p>
      </main>
    );
  }

  return (
    <main className="max-w-5xl mx-auto px-4 py-12">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Components</h1>
      <p className="text-sm text-gray-500 mb-6">
        Per-unit carbon footprint. Expand a component to see materials and production blocks.
      </p>
      <ComponentsTable components={components} />
    </main>
  );
}
