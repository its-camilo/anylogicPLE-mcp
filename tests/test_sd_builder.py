"""Tests for System Dynamics .alp XML builder."""

import xml.etree.ElementTree as ET

import pytest

from anylogic_mcp.sd_builder import SDModelBuilder
from anylogic_mcp.sd_templates import build_template


@pytest.fixture
def sd_builder():
    return SDModelBuilder()


def xml(data: bytes) -> str:
    return data.decode("utf-8")


class TestSDBuiler:
    def test_predator_prey_generates_valid_xml(self, sd_builder):
        definition = build_template("predator_prey", {})
        out = xml(sd_builder.build_model(definition))
        assert '<?xml version="1.0"' in out
        assert "<AnyLogicWorkspace" in out
        ET.fromstring(out)

    def test_contains_sd_elements(self, sd_builder):
        definition = build_template("predator_prey", {})
        out = xml(sd_builder.build_model(definition))
        assert 'Class="StockVariable"' in out
        assert 'Class="Flow"' in out
        assert 'Class="AuxVariable"' in out
        assert 'Class="Parameter"' in out
        assert "<Dependences>" in out
        assert "<TableFunctions>" in out
        assert "<TimePlot>" in out

    def test_flow_source_target_ids(self, sd_builder):
        definition = build_template("simple_stock_flow", {})
        out = xml(sd_builder.build_model(definition))
        assert 'TargetId="' in out
        assert 'SourceId="' in out
        assert "<![CDATA[Inventory]]>" in out

    def test_year_time_unit(self, sd_builder):
        definition = build_template("food_security_malaysia", {})
        out = xml(sd_builder.build_model(definition))
        assert "<ModelTimeUnit><![CDATA[Year]]></ModelTimeUnit>" in out
        assert "<FinalTime><![CDATA[50.0]]></FinalTime>" in out

    def test_unique_ids(self, sd_builder):
        definition = build_template("food_security_malaysia", {})
        out = xml(sd_builder.build_model(definition))
        import re
        ids = re.findall(r"<Id>(\d+)</Id>", out)
        assert len(ids) == len(set(ids))

    def test_build_from_template(self, sd_builder):
        out = xml(sd_builder.build_from_template("predator_prey", {}))
        assert "<![CDATA[Hares]]>" in out
