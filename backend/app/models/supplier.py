import uuid
from ..db import db


def gen_uuid():
    return str(uuid.uuid4())


class Supplier(db.Model):
    __tablename__ = "suppliers"

    supplier_id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    supplier_name = db.Column(db.String(255), nullable=False, unique=True)

    materials = db.relationship("Material", back_populates="supplier")
