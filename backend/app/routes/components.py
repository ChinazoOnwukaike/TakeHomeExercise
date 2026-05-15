from flask import Blueprint, jsonify, abort
from ..db import db
from ..models import Component
from .serializers import serialize_material

bp = Blueprint("components", __name__, url_prefix="/api/components")


@bp.get("/", strict_slashes=False)
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


@bp.get("/<string:component_id>")
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
        "materials": [serialize_material(m) for m in c.materials],
    })
