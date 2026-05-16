import pytest
from app.models import Supplier, Component, Material, Block
from app.routes.blocks import _recompute_component


@pytest.fixture
def full_seed(db):
    """Full dataset mirroring the three CSVs — used to verify computed footprints."""
    acme    = Supplier(supplier_name="AcmeSteel")
    alpha   = Supplier(supplier_name="AlphaAl")
    wire    = Supplier(supplier_name="GlobalWire")
    polymer = Supplier(supplier_name="PolymerCo")
    eco     = Supplier(supplier_name="EcoCoat")
    db.session.add_all([acme, alpha, wire, polymer, eco])
    db.session.flush()

    c001 = Component(sku="c-001", component_name="Industrial Pump Assembly")
    c002 = Component(sku="c-002", component_name="Aluminum Frame")
    c003 = Component(sku="c-003", component_name="Steel Bracket")
    db.session.add_all([c001, c002, c003])
    db.session.flush()

    # c-001 materials
    steel_001   = Material(component_id=c001.component_id, material_name="steel",   weight=1250, supplier_id=acme.supplier_id)
    copper_001  = Material(component_id=c001.component_id, material_name="copper",  weight=200,  supplier_id=wire.supplier_id)
    plastic_001 = Material(component_id=c001.component_id, material_name="plastic", weight=350,  supplier_id=polymer.supplier_id)
    paint_001   = Material(component_id=c001.component_id, material_name="paint",   weight=40,   supplier_id=eco.supplier_id)

    # c-002 materials
    alum_002  = Material(component_id=c002.component_id, material_name="aluminum", weight=800,  supplier_id=alpha.supplier_id)
    steel_002 = Material(component_id=c002.component_id, material_name="steel",    weight=150,  supplier_id=acme.supplier_id)

    # c-003 materials
    steel_003 = Material(component_id=c003.component_id, material_name="steel", weight=250, supplier_id=None)

    db.session.add_all([steel_001, copper_001, plastic_001, paint_001, alum_002, steel_002, steel_003])
    db.session.flush()

    blocks = [
        # steel c-001 (AcmeSteel supplier-reported)
        Block(material_id=steel_001.material_id, block_name="raw_production", co2e_value=165, supplier_reported_co2e_value=150),
        Block(material_id=steel_001.material_id, block_name="processing",     co2e_value=35,  supplier_reported_co2e_value=30),
        Block(material_id=steel_001.material_id, block_name="coating",        co2e_value=10,  supplier_reported_co2e_value=5),

        # copper c-001 (GlobalWire supplier-reported)
        Block(material_id=copper_001.material_id, block_name="extraction", co2e_value=380, supplier_reported_co2e_value=280),
        Block(material_id=copper_001.material_id, block_name="refining",   co2e_value=80,  supplier_reported_co2e_value=60),

        # plastic c-001 (no supplier-reported)
        Block(material_id=plastic_001.material_id, block_name="polymerization", co2e_value=230, supplier_reported_co2e_value=None),
        Block(material_id=plastic_001.material_id, block_name="molding",        co2e_value=50,  supplier_reported_co2e_value=None),

        # paint c-001 (no supplier-reported)
        Block(material_id=paint_001.material_id, block_name="production", co2e_value=450, supplier_reported_co2e_value=None),

        # aluminum c-002 (AlphaAl supplier-reported)
        Block(material_id=alum_002.material_id, block_name="mining",   co2e_value=120, supplier_reported_co2e_value=80),
        Block(material_id=alum_002.material_id, block_name="smelting", co2e_value=900, supplier_reported_co2e_value=650),
        Block(material_id=alum_002.material_id, block_name="rolling",  co2e_value=130, supplier_reported_co2e_value=90),

        # steel c-002 (AcmeSteel supplier-reported)
        Block(material_id=steel_002.material_id, block_name="raw_production", co2e_value=165, supplier_reported_co2e_value=150),
        Block(material_id=steel_002.material_id, block_name="processing",     co2e_value=35,  supplier_reported_co2e_value=30),
        Block(material_id=steel_002.material_id, block_name="coating",        co2e_value=10,  supplier_reported_co2e_value=5),

        # steel c-003 (no supplier — industry default only)
        Block(material_id=steel_003.material_id, block_name="raw_production", co2e_value=165, supplier_reported_co2e_value=None),
        Block(material_id=steel_003.material_id, block_name="processing",     co2e_value=35,  supplier_reported_co2e_value=None),
        Block(material_id=steel_003.material_id, block_name="coating",        co2e_value=10,  supplier_reported_co2e_value=None),
    ]
    db.session.add_all(blocks)
    db.session.commit()

    return {"c001": c001, "c002": c002, "c003": c003}


class TestFootprintAccuracy:
    def test_c001_industrial_pump(self, db, full_seed):
        # steel 12.5 × 1.85 + copper 2.0 × 3.40 + plastic 3.5 × 2.80 + paint 0.4 × 4.50
        # = 23.125 + 6.80 + 9.80 + 1.80 = 41.525
        _recompute_component(full_seed["c001"].component_id)
        from app.models import Component
        result = db.session.get(Component, full_seed["c001"].component_id)
        assert float(result.total_footprint) == pytest.approx(41.525)

    def test_c002_aluminum_frame(self, db, full_seed):
        # aluminum 8.0 × 8.20 + steel 1.5 × 1.85
        # = 65.60 + 2.775 = 68.375
        _recompute_component(full_seed["c002"].component_id)
        from app.models import Component
        result = db.session.get(Component, full_seed["c002"].component_id)
        assert float(result.total_footprint) == pytest.approx(68.375)

    def test_c003_steel_bracket(self, db, full_seed):
        # steel 2.5 × 2.10 (industry default — no supplier)
        # = 5.25
        _recompute_component(full_seed["c003"].component_id)
        from app.models import Component
        result = db.session.get(Component, full_seed["c003"].component_id)
        assert float(result.total_footprint) == pytest.approx(5.25)
