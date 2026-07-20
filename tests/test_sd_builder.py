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

    def test_has_agent_links_matching_connections_id(self, sd_builder):
        """AnyLogic crashes on open if ConnectionsId has no matching AgentLinks."""
        import re

        definition = build_template("predator_prey", {})
        out = xml(sd_builder.build_model(definition))
        assert "<AgentLinks>" in out
        assert "<AgentLink>" in out
        assert "<![CDATA[connections]]>" in out

        conn_match = re.search(r"<ConnectionsId>(\d+)</ConnectionsId>", out)
        assert conn_match is not None
        conn_id = conn_match.group(1)
        # AgentLink Id must equal ConnectionsId
        assert f"<AgentLink>\n\t\t\t\t\t<Id>{conn_id}</Id>" in out or (
            f"<Id>{conn_id}</Id>" in out
            and out.find("<AgentLinks>") < out.find(f"<Id>{conn_id}</Id>")
        )

    def test_has_converters_applied_outside_model(self, sd_builder):
        definition = build_template("simple_stock_flow", {})
        out = xml(sd_builder.build_model(definition))
        assert "<ConvertersApplied>" in out
        assert "</Model>" in out
        assert out.find("</Model>") < out.find("<ConvertersApplied>")
        assert "<BypassInitialScreen>true</BypassInitialScreen>" in out

    def test_agent_links_before_presentation(self, sd_builder):
        definition = build_template("food_security_malaysia", {})
        out = xml(sd_builder.build_model(definition))
        assert out.find("<TableFunctions>") < out.find("<AgentLinks>")
        assert out.find("<AgentLinks>") < out.find("<Presentation>")
