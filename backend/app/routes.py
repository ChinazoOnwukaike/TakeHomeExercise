from flask import Blueprint, jsonify, request, abort
from .db import db
from .models import Component, Material, Block, Supplier

bp = Blueprint("api", __name__, url_prefix="/api")


def _recompute_component(component_id: str) -> None:
    materials = Material.query.filter_by(component_id=component_id).all()
    total = 0.0
    for mat in materials:
        blocks = Block.query.filter_by(material_id=mat.material_id).all()
        block_sum = sum(
            b.supplier_reported_co2e_value if b.supplier_reported_co2e_value is not None else b.co2e_value
            for b in blocks
        )
        total += (mat.weight / 100) * (block_sum / 100)
    component = db.session.get(Component, component_id)
    component.total_footprint = round(total, 6)
    db.session.commit()


def _serialize_block(b: Block) -> dict:
    active = b.supplier_reported_co2e_value if b.supplier_reported_co2e_value is not None else b.co2e_value
    return {
        "block_id": b.block_id,
        "block_name": b.block_name,
        "co2e_value": b.co2e_value / 100,
        "supplier_reported_co2e_value": b.supplier_reported_co2e_value / 100 if b.supplier_reported_co2e_value is not None else None,
        "active_co2e": active / 100,
        "source": "supplier-reported" if b.supplier_reported_co2e_value is not None else "industry-default",
    }


def _serialize_material(mat: Material) -> dict:
    supplier_name = mat.supplier.supplier_name if mat.supplier else None
    return {
        "material_id": mat.material_id,
        "material_name": mat.material_name,
        "weight": mat.weight / 100,
        "supplier_name": supplier_name,
        "blocks": [_serialize_block(b) for b in mat.blocks],
    }


@bp.get("/components")
def list_components():
    components = Component.query.order_by(Component.sku).all()
    return jsonify([
        {
            "component_id": c.component_id,
            "sku": c.sku,
            "component_name": c.component_name,
            "description": c.description,
            "total_footprint": float(c.total_footprint) if c.total_footprint is not None else None,
        }
        for c in components
    ])


@bp.get("/components/<string:component_id>")
def get_component(component_id: str):
    c = db.session.get(Component, component_id)
    if not c:
        abort(404)
    return jsonify({
        "component_id": c.component_id,
        "sku": c.sku,
        "component_name": c.component_name,
        "description": c.description,
        "total_footprint": float(c.total_footprint) if c.total_footprint is not None else None,
        "materials": [_serialize_material(m) for m in c.materials],
    })


@bp.patch("/blocks/<string:block_id>")
def update_block(block_id: str):
    block = db.session.get(Block, block_id)
    if not block:
        abort(404)

    body = request.get_json(silent=True) or {}
    if "supplier_reported_co2e_value" not in body:
        abort(400)

    raw = body["supplier_reported_co2e_value"]
    if raw is None:
        block.supplier_reported_co2e_value = None
    else:
        try:
            block.supplier_reported_co2e_value = round(float(raw) * 100)
        except (TypeError, ValueError):
            abort(400)

    db.session.commit()

    component_id = block.material.component_id
    _recompute_component(component_id)

    c = db.session.get(Component, component_id)
    return jsonify({
        "block": _serialize_block(block),
        "total_footprint": float(c.total_footprint),
    })
