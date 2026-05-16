import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from app import create_app
from app.db import db as _db
from app.models import Supplier, Component, Material, Block


@pytest.fixture(scope="session")
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture
def seed_data(db):
    supplier = Supplier(supplier_name="AcmeSteel")
    db.session.add(supplier)
    db.session.flush()

    component = Component(
        sku="c-001",
        component_name="Industrial Pump Assembly",
        description="Centrifugal water pump for manufacturing",
    )
    db.session.add(component)
    db.session.flush()

    material = Material(
        component_id=component.component_id,
        material_name="steel",
        weight=1250,  # 12.5 kg × 100
        supplier_id=supplier.supplier_id,
    )
    db.session.add(material)
    db.session.flush()

    blocks = [
        Block(material_id=material.material_id, block_name="raw_production",   co2e_value=165, supplier_reported_co2e_value=150),
        Block(material_id=material.material_id, block_name="transportation",   co2e_value=35,  supplier_reported_co2e_value=30),
        Block(material_id=material.material_id, block_name="waste_processing", co2e_value=10,  supplier_reported_co2e_value=5),
    ]
    for b in blocks:
        db.session.add(b)
    db.session.commit()

    return {"supplier": supplier, "component": component, "material": material, "blocks": blocks}
