import uuid
from ..db import db


def gen_uuid():
    return str(uuid.uuid4())


class Block(db.Model):
    __tablename__ = "blocks"

    block_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    block_name = db.Column(db.String(255), nullable=False)
    material_id = db.Column(db.String(36), db.ForeignKey("materials.material_id"), nullable=False)
    co2e_value = db.Column(db.Integer, nullable=False)           # industry default × 100
    supplier_reported_co2e_value = db.Column(db.Integer, nullable=True)  # supplier value × 100; used if not null

    material = db.relationship("Material", back_populates="blocks")
