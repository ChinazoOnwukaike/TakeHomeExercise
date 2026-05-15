"""
Seed the database from the three CSVs in ../seed-data/.

Run from the backend/ directory:
    python seed.py
"""
import csv
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.db import db
from app.models import Supplier, Component, Material, Block

SEED_DIR = Path(__file__).parent.parent / "seed-data"


def load_csv(name: str) -> list[dict]:
    with open(SEED_DIR / name, newline="") as f:
        return list(csv.DictReader(f))


def to_int100(value: str) -> int:
    """Convert a decimal string to integer × 100 (e.g. '0.80' → 80, '12.5' → 1250)."""
    return round(float(value) * 100)


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        components_csv = load_csv("components.csv")
        materials_csv = load_csv("component_materials.csv")
        blocks_csv = load_csv("blocks.csv")

        # --- Suppliers ---
        # Collect all non-empty supplier names from materials CSV
        supplier_names = {row["supplier"] for row in materials_csv if row["supplier"].strip()}
        supplier_map: dict[str, str] = {}  # name → supplier_id

        for name in sorted(supplier_names):
            s = Supplier(supplier_id=str(uuid.uuid4()), supplier_name=name)
            db.session.add(s)
            supplier_map[name] = s.supplier_id

        db.session.flush()

        # --- Components ---
        component_map: dict[str, str] = {}  # sku (e.g. "c-001") → component_id UUID

        for row in components_csv:
            c = Component(
                component_id=str(uuid.uuid4()),
                sku=row["component_id"],
                component_name=row["name"],
                description=row.get("description", "").strip() or None,
            )
            db.session.add(c)
            component_map[row["component_id"]] = c.component_id

        db.session.flush()

        # --- Build block lookup from blocks CSV ---
        # Structure: blocks_by_material[material_name][block_name] = {
        #   "default": <kg_co2e_per_unit str>,
        #   "supplier": { supplier_name: <kg_co2e_per_unit str> }
        # }
        blocks_by_material: dict[str, dict[str, dict]] = {}
        for row in blocks_csv:
            mat = row["material"]
            bname = row["block_name"]
            supplier = row["supplier"].strip()
            value = row["kg_co2e_per_unit"]

            if mat not in blocks_by_material:
                blocks_by_material[mat] = {}
            if bname not in blocks_by_material[mat]:
                blocks_by_material[mat][bname] = {"default": None, "supplier": {}}

            if supplier == "":
                blocks_by_material[mat][bname]["default"] = value
            else:
                blocks_by_material[mat][bname]["supplier"][supplier] = value

        # --- Materials + Blocks ---
        for row in materials_csv:
            csv_sku = row["component_id"]
            mat_name = row["material"]
            supplier_name = row["supplier"].strip()
            weight_int = to_int100(row["weight"])

            supplier_id = supplier_map.get(supplier_name) if supplier_name else None
            component_id = component_map[csv_sku]

            mat = Material(
                material_id=str(uuid.uuid4()),
                component_id=component_id,
                material_name=mat_name,
                weight=weight_int,
                supplier_id=supplier_id,
            )
            db.session.add(mat)
            db.session.flush()

            block_data = blocks_by_material.get(mat_name, {})
            for block_name, values in block_data.items():
                default_val = values.get("default")
                if default_val is None:
                    continue  # no industry default — skip

                co2e_int = to_int100(default_val)

                supplier_reported_int = None
                if supplier_name and supplier_name in values["supplier"]:
                    supplier_reported_int = to_int100(values["supplier"][supplier_name])

                b = Block(
                    block_id=str(uuid.uuid4()),
                    block_name=block_name,
                    material_id=mat.material_id,
                    co2e_value=co2e_int,
                    supplier_reported_co2e_value=supplier_reported_int,
                )
                db.session.add(b)

        db.session.flush()

        # --- Compute initial total_footprint for all components ---
        for sku, component_id in component_map.items():
            mats = Material.query.filter_by(component_id=component_id).all()
            total = 0.0
            for m in mats:
                blks = Block.query.filter_by(material_id=m.material_id).all()
                block_sum = sum(
                    b.supplier_reported_co2e_value if b.supplier_reported_co2e_value is not None else b.co2e_value
                    for b in blks
                )
                total += (m.weight / 100) * (block_sum / 100)
            c = db.session.get(Component, component_id)
            c.total_footprint = round(total, 6)

        db.session.commit()
        print("Seed complete.")
        print_summary()


def print_summary():
    from app import create_app
    app = create_app()
    with app.app_context():
        for c in Component.query.order_by(Component.sku).all():
            print(f"  {c.sku} ({c.component_name}): total_footprint = {c.total_footprint}")


if __name__ == "__main__":
    seed()
