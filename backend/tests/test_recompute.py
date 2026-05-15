import pytest
from app.routes.blocks import _recompute_component
from app.models import Component
from app.db import db


class TestRecomputeComponent:
    def test_uses_supplier_reported_when_present(self, db, seed_data):
        # steel: 12.5 kg, blocks sum = 150+30+5 = 185 → /100 = 1.85
        # total = (1250/100) * (185/100) = 12.5 * 1.85 = 23.125
        component = seed_data["component"]
        _recompute_component(component.component_id)
        result = db.session.get(Component, component.component_id)
        assert float(result.total_footprint) == pytest.approx(23.125)

    def test_falls_back_to_industry_default_when_supplier_cleared(self, db, seed_data):
        # clear all supplier values → use co2e_value: 165+35+10 = 210 → /100 = 2.10
        # total = 12.5 * 2.10 = 26.25
        for block in seed_data["blocks"]:
            block.supplier_reported_co2e_value = None
        db.session.commit()

        component = seed_data["component"]
        _recompute_component(component.component_id)
        result = db.session.get(Component, component.component_id)
        assert float(result.total_footprint) == pytest.approx(26.25)

    def test_partial_supplier_data(self, db, seed_data):
        # clear supplier on first block only → 165 + 30 + 5 = 200 → /100 = 2.00
        # total = 12.5 * 2.00 = 25.0
        seed_data["blocks"][0].supplier_reported_co2e_value = None
        db.session.commit()

        component = seed_data["component"]
        _recompute_component(component.component_id)
        result = db.session.get(Component, component.component_id)
        assert float(result.total_footprint) == pytest.approx(25.0)
