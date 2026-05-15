from ..models import Block, Material

# Change from the SQLAlchemy model to py dicts for Flask JSON
def serialize_block(b: Block) -> dict:
    active = b.supplier_reported_co2e_value if b.supplier_reported_co2e_value is not None else b.co2e_value
    return {
        "block_id": b.block_id,
        "block_name": b.block_name,
        "co2e_value": b.co2e_value / 100,
        "supplier_reported_co2e_value": b.supplier_reported_co2e_value / 100 if b.supplier_reported_co2e_value is not None else None,
        "active_co2e": active / 100,
        "source": "supplier-reported" if b.supplier_reported_co2e_value is not None else "industry-default",
    }


def serialize_material(mat: Material) -> dict:
    supplier_name = mat.supplier.supplier_name if mat.supplier else None
    return {
        "material_id": mat.material_id,
        "material_name": mat.material_name,
        "weight": mat.weight / 100,
        "supplier_name": supplier_name,
        "blocks": sorted(
            [serialize_block(b) for b in mat.blocks],
            key=lambda x: x["active_co2e"],
            reverse=True,
        ),
    }
