import uuid
from .db import db


def gen_uuid():
    return str(uuid.uuid4())


class Supplier(db.Model):
    __tablename__ = "suppliers"

    supplier_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    supplier_name = db.Column(db.String(255), nullable=False, unique=True)

    materials = db.relationship("Material", back_populates="supplier")


class Component(db.Model):
    __tablename__ = "components"

    component_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    sku = db.Column(db.String(50), nullable=False, unique=True)
    component_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    total_footprint = db.Column(db.Numeric(precision=18, scale=6), nullable=True)

    materials = db.relationship("Material", back_populates="component")


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


class Block(db.Model):
    __tablename__ = "blocks"

    block_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    block_name = db.Column(db.String(255), nullable=False)
    material_id = db.Column(db.String(36), db.ForeignKey("materials.material_id"), nullable=False)
    co2e_value = db.Column(db.Integer, nullable=False)           # industry default × 100
    supplier_reported_co2e_value = db.Column(db.Integer, nullable=True)  # supplier value × 100; used if not null

    material = db.relationship("Material", back_populates="blocks")
