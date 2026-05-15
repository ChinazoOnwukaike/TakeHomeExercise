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
    <>
      <header className="bg-white border-b border-gray-200 px-8 py-4 flex items-center gap-3">
        <span className="text-brand-dark font-bold text-lg tracking-widest uppercase">Terralytiq</span>
      </header>
      <main className="max-w-7xl mx-auto w-full px-8 py-10">
        <h1 className="text-2xl font-bold text-brand-dark mb-1">Components</h1>
        <p className="text-sm text-brand-muted mb-6">
          Per-unit carbon footprint. Expand a component to see materials and production blocks.
        </p>
        <ComponentsTable components={components} />
      </main>
    </>
  );
}
