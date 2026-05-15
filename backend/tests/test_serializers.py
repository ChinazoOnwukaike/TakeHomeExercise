import pytest
from app.routes.serializers import serialize_block, serialize_material
from app.models import Block, Material, Supplier, Component
from app.db import db


def make_block(material_id, co2e_value, supplier_reported_co2e_value=None):
    b = Block(
        material_id=material_id,
        block_name="test_block",
        co2e_value=co2e_value,
        supplier_reported_co2e_value=supplier_reported_co2e_value,
    )
    db.session.add(b)
    db.session.flush()
    return b


class TestSerializeBlock:
    def test_industry_default_source(self, db, seed_data):
        block = make_block(seed_data["material"].material_id, co2e_value=150)
        result = serialize_block(block)
        assert result["source"] == "industry-default"

    def test_supplier_reported_source(self, db, seed_data):
        block = make_block(seed_data["material"].material_id, co2e_value=165, supplier_reported_co2e_value=150)
        result = serialize_block(block)
        assert result["source"] == "supplier-reported"

    def test_active_co2e_uses_industry_default_when_no_supplier(self, db, seed_data):
        block = make_block(seed_data["material"].material_id, co2e_value=200)
        result = serialize_block(block)
        assert result["active_co2e"] == pytest.approx(2.00)

    def test_active_co2e_uses_supplier_value_when_present(self, db, seed_data):
        block = make_block(seed_data["material"].material_id, co2e_value=200, supplier_reported_co2e_value=150)
        result = serialize_block(block)
        assert result["active_co2e"] == pytest.approx(1.50)

    def test_values_divided_by_100(self, db, seed_data):
        block = make_block(seed_data["material"].material_id, co2e_value=80, supplier_reported_co2e_value=60)
        result = serialize_block(block)
        assert result["co2e_value"] == pytest.approx(0.80)
        assert result["supplier_reported_co2e_value"] == pytest.approx(0.60)

    def test_supplier_reported_co2e_is_none_when_not_set(self, db, seed_data):
        block = make_block(seed_data["material"].material_id, co2e_value=100)
        result = serialize_block(block)
        assert result["supplier_reported_co2e_value"] is None


class TestSerializeMaterial:
    def test_blocks_sorted_by_active_co2e_descending(self, db, seed_data):
        material = seed_data["material"]
        result = serialize_material(material)
        values = [b["active_co2e"] for b in result["blocks"]]
        assert values == sorted(values, reverse=True)

    def test_supplier_name_included(self, db, seed_data):
        result = serialize_material(seed_data["material"])
        assert result["supplier_name"] == "AcmeSteel"

    def test_supplier_name_none_when_no_supplier(self, db, seed_data):
        component = seed_data["component"]
        material_no_supplier = Material(
            component_id=component.component_id,
            material_name="paint",
            weight=40,
            supplier_id=None,
        )
        db.session.add(material_no_supplier)
        db.session.flush()
        result = serialize_material(material_no_supplier)
        assert result["supplier_name"] is None

    def test_weight_divided_by_100(self, db, seed_data):
        result = serialize_material(seed_data["material"])
        assert result["weight"] == pytest.approx(12.5)
