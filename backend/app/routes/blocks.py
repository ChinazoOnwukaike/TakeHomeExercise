from flask import Blueprint, jsonify, request, abort
from ..db import db
from ..models import Component, Material, Block
from .serializers import serialize_block

bp = Blueprint("blocks", __name__, url_prefix="/api/blocks")


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


@bp.patch("/<string:block_id>")
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
        "block": serialize_block(block),
        "total_footprint": float(c.total_footprint),
    })
