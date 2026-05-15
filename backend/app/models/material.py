import uuid
from ..db import db


def gen_uuid():
    return str(uuid.uuid4())


class Material(db.Model):
    __tablename__ = "materials"

    material_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    component_id = db.Column(db.String(36), db.ForeignKey("components.component_id"), nullable=False)
    material_name = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.Integer, nullable=False)  # stored × 100 (e.g. 12.5kg → 1250)
    supplier_id = db.Column(db.String(36), db.ForeignKey("suppliers.supplier_id"), nullable=True)

    component = db.relationship("Component", back_populates="materials")
    supplier = db.relationship("Supplier", back_populates="materials")
    blocks = db.relationship("Block", back_populates="material")
