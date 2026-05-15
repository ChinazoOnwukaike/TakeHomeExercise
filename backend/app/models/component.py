import uuid
from ..db import db


def gen_uuid():
    return str(uuid.uuid4())


class Component(db.Model):
    __tablename__ = "components"

    component_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    sku = db.Column(db.String(50), nullable=False, unique=True)
    component_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    total_footprint = db.Column(db.Numeric(precision=18, scale=6), nullable=True)

    materials = db.relationship("Material", back_populates="component")
