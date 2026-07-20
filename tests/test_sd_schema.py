"""Tests for System Dynamics schema validation."""

import pytest
from pydantic import ValidationError

from anylogic_mcp.sd_schema import (
    AuxDef,
    FlowDef,
    LinkDef,
    SDModelDefinition,
    StockDef,
)


def _minimal_sd(**overrides):
    base = {
        "name": "Test",
        "description": "Test model",
        "time_unit": "Year",
        "duration": 10,
        "stocks": [
            StockDef(name="Inventory", initial_value="100", expression="inflow - outflow"),
        ],
        "flows": [
            FlowDef(name="inflow", formula="1", target="Inventory"),
            FlowDef(name="outflow", formula="0.5", source="Inventory"),
        ],
        "links": [
            LinkDef(source="inflow", target="Inventory"),
            LinkDef(source="Inventory", target="outflow"),
        ],
    }
    base.update(overrides)
    return SDModelDefinition(**base)


class TestSDSchema:
    def test_valid_minimal_model(self):
        model = _minimal_sd()
        assert model.variable_count() == 3

    def test_auto_stock_expression(self):
        model = SDModelDefinition(
            name="Auto",
            description="Auto expression",
            duration=10,
            stocks=[StockDef(name="X", initial_value="0")],
            flows=[
                FlowDef(name="in", formula="1", target="X"),
                FlowDef(name="out", formula="0.5", source="X"),
            ],
            links=[
                LinkDef(source="in", target="X"),
                LinkDef(source="X", target="out"),
            ],
        )
        assert model.stock_expressions()["X"] == "in + -out"

    def test_rejects_duplicate_names(self):
        with pytest.raises(ValidationError, match="Duplicate name"):
            _minimal_sd(
                auxiliaries=[AuxDef(name="Inventory", formula="1")],
            )

    def test_rejects_unknown_flow_source(self):
        with pytest.raises(ValidationError, match="not a defined stock"):
            _minimal_sd(
                flows=[FlowDef(name="bad", formula="1", source="Missing")],
            )

    def test_rejects_unknown_formula_ref(self):
        with pytest.raises(ValidationError, match="unknown identifier|not a defined"):
            SDModelDefinition(
                name="Test",
                description="Test",
                duration=10,
                stocks=[StockDef(name="Inventory", initial_value="100", expression="inflow")],
                flows=[FlowDef(name="inflow", formula="unknownVar", target="Inventory")],
                links=[LinkDef(source="inflow", target="Inventory")],
            )

    def test_rejects_unsafe_formula(self):
        with pytest.raises(ValidationError, match="disallowed"):
            _minimal_sd(
                flows=[FlowDef(name="inflow", formula="new Object()", target="Inventory")],
            )

    def test_rejects_invalid_java_name(self):
        with pytest.raises(ValidationError, match="valid Java identifier"):
            _minimal_sd(
                stocks=[StockDef(name="123bad", initial_value="0", expression="0")],
            )

    def test_to_store_dict(self):
        model = _minimal_sd()
        store = model.to_store_dict("test-id")
        assert store["paradigm"] == "system_dynamics"
        assert store["uses_process_library"] is False
        assert store["system_dynamics"]["variable_count"] == 3
