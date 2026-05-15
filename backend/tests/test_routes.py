import json
import pytest


class TestListComponents:
    def test_returns_200(self, client, seed_data):
        res = client.get("/api/components")
        assert res.status_code == 200

    def test_returns_all_components(self, client, seed_data):
        res = client.get("/api/components")
        data = res.get_json()
        assert len(data) == 1
        assert data[0]["sku"] == "c-001"

    def test_response_shape(self, client, seed_data):
        data = client.get("/api/components").get_json()
        keys = {"component_id", "sku", "component_name", "description", "total_footprint"}
        assert keys.issubset(data[0].keys())


class TestGetComponent:
    def test_returns_200(self, client, seed_data):
        component_id = seed_data["component"].component_id
        res = client.get(f"/api/components/{component_id}")
        assert res.status_code == 200

    def test_returns_404_for_unknown_id(self, client, seed_data):
        res = client.get("/api/components/nonexistent-id")
        assert res.status_code == 404

    def test_includes_nested_materials_and_blocks(self, client, seed_data):
        component_id = seed_data["component"].component_id
        data = client.get(f"/api/components/{component_id}").get_json()
        assert len(data["materials"]) == 1
        assert len(data["materials"][0]["blocks"]) == 3

    def test_blocks_sorted_by_active_co2e_descending(self, client, seed_data):
        component_id = seed_data["component"].component_id
        data = client.get(f"/api/components/{component_id}").get_json()
        values = [b["active_co2e"] for b in data["materials"][0]["blocks"]]
        assert values == sorted(values, reverse=True)


class TestUpdateBlock:
    def test_returns_200_on_valid_update(self, client, seed_data):
        block_id = seed_data["blocks"][0].block_id
        res = client.patch(
            f"/api/blocks/{block_id}",
            data=json.dumps({"supplier_reported_co2e_value": 1.20}),
            content_type="application/json",
        )
        assert res.status_code == 200

    def test_updates_block_value(self, client, seed_data):
        block_id = seed_data["blocks"][0].block_id
        data = client.patch(
            f"/api/blocks/{block_id}",
            data=json.dumps({"supplier_reported_co2e_value": 1.20}),
            content_type="application/json",
        ).get_json()
        assert data["block"]["supplier_reported_co2e_value"] == pytest.approx(1.20)

    def test_returns_updated_total_footprint(self, client, seed_data):
        block_id = seed_data["blocks"][0].block_id
        data = client.patch(
            f"/api/blocks/{block_id}",
            data=json.dumps({"supplier_reported_co2e_value": 1.20}),
            content_type="application/json",
        ).get_json()
        assert "total_footprint" in data
        assert isinstance(data["total_footprint"], float)

    def test_clearing_supplier_value_falls_back_to_default(self, client, seed_data):
        block_id = seed_data["blocks"][0].block_id
        data = client.patch(
            f"/api/blocks/{block_id}",
            data=json.dumps({"supplier_reported_co2e_value": None}),
            content_type="application/json",
        ).get_json()
        assert data["block"]["source"] == "industry-default"
        assert data["block"]["supplier_reported_co2e_value"] is None

    def test_returns_400_when_key_missing(self, client, seed_data):
        block_id = seed_data["blocks"][0].block_id
        res = client.patch(
            f"/api/blocks/{block_id}",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert res.status_code == 400

    def test_returns_400_for_invalid_value(self, client, seed_data):
        block_id = seed_data["blocks"][0].block_id
        res = client.patch(
            f"/api/blocks/{block_id}",
            data=json.dumps({"supplier_reported_co2e_value": "not-a-number"}),
            content_type="application/json",
        )
        assert res.status_code == 400

    def test_returns_404_for_unknown_block(self, client, seed_data):
        res = client.patch(
            "/api/blocks/nonexistent-id",
            data=json.dumps({"supplier_reported_co2e_value": 1.0}),
            content_type="application/json",
        )
        assert res.status_code == 404
