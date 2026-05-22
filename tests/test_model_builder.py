"""Tests for AnyLogic model builder — .alp XML generation."""

import pytest
from anylogic_mcp.model_builder import AnyLogicModelBuilder, ModelDefinition


@pytest.fixture
def builder():
    return AnyLogicModelBuilder()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def xml(data: bytes) -> str:
    return data.decode("utf-8")


# ---------------------------------------------------------------------------
# Template smoke tests — all four must generate valid XML
# ---------------------------------------------------------------------------

class TestTemplates:
    def test_warehouse_generates_xml(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert '<?xml version="1.0"' in out
        assert "<AnyLogicWorkspace" in out

    def test_simple_queue_generates_xml(self, builder):
        out = xml(builder.build_from_template("simple_queue", {"name": "Q"}))
        assert "<AnyLogicWorkspace" in out

    def test_factory_generates_xml(self, builder):
        out = xml(builder.build_from_template("factory", {"name": "F"}))
        assert "<AnyLogicWorkspace" in out

    def test_hospital_generates_xml(self, builder):
        out = xml(builder.build_from_template("hospital", {"name": "H"}))
        assert "<AnyLogicWorkspace" in out

    def test_unknown_template_raises(self, builder):
        with pytest.raises(ValueError, match="Unknown template"):
            builder.build_from_template("nonexistent", {})


# ---------------------------------------------------------------------------
# Block structure — correct types in the flow
# ---------------------------------------------------------------------------

class TestBlockStructure:
    def test_warehouse_has_source_queue_delay_sink(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        # All four block types must appear as EmbeddedObject ClassName entries
        for btype in ("Source", "Queue", "Delay", "Sink"):
            assert f"<ClassName><![CDATA[{btype}]]></ClassName>" in out

    def test_factory_has_two_delays(self, builder):
        out = xml(builder.build_from_template("factory", {"name": "F"}))
        # Each Delay EmbeddedObject has exactly one GPS with ItemName 1412336242930
        assert out.count("<![CDATA[1412336242930]]>") == 2

    def test_factory_has_two_queues(self, builder):
        out = xml(builder.build_from_template("factory", {"name": "F"}))
        # Each Queue EmbeddedObject has exactly one GPS with ItemName 1412336242932
        assert out.count("<![CDATA[1412336242932]]>") == 2

    def test_hospital_has_two_delays(self, builder):
        out = xml(builder.build_from_template("hospital", {"name": "H"}))
        assert out.count("<![CDATA[1412336242930]]>") == 2

    def test_queue_auto_injected_before_delay(self, builder):
        """Queue block name must be <delayName>Queue."""
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        # Delay is named "service" → auto-Queue is "serviceQueue"
        assert "<![CDATA[serviceQueue]]>" in out

    def test_no_service_blocks(self, builder):
        """Service blocks are not used — all serving is done via Delay."""
        for tname in ("warehouse", "simple_queue", "factory", "hospital"):
            out = xml(builder.build_from_template(tname, {"name": "X"}))
            assert "<ClassName><![CDATA[Service]]></ClassName>" not in out


# ---------------------------------------------------------------------------
# Parameter correctness
# ---------------------------------------------------------------------------

class TestParameters:
    def test_delay_time_param_name_is_delayTime(self, builder):
        """Parameter must be 'delayTime', not 'delay'."""
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "<![CDATA[delayTime]]>" in out
        assert "<![CDATA[delay]]>" not in out

    def test_delay_time_unit_is_minute(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "<![CDATA[MINUTE]]>" in out

    def test_queue_capacity_is_100000(self, builder):
        """Queue capacity must be explicitly set to prevent OOM and default-100 issues."""
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "<![CDATA[100000]]>" in out

    def test_interarrival_uses_rate_form(self, builder):
        """interarrivalTime must use 1/mean form, not the mean directly."""
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        # Warehouse uses exponential(1.0/20.0)
        assert "1.0/20.0" in out
        # Must NOT use the bare mean (exponential(20))
        assert "exponential(20)" not in out

    def test_warehouse_arrival_type_is_interarrival_time(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "self.INTERARRIVAL_TIME" in out

    def test_warehouse_num_docks_param(self, builder):
        out = xml(builder.build_from_template("warehouse", {"num_docks": 5, "name": "W"}))
        assert "<![CDATA[5]]>" in out

    def test_factory_machine_names(self, builder):
        out = xml(builder.build_from_template("factory", {"name": "F"}))
        assert "<![CDATA[machineA]]>" in out
        assert "<![CDATA[machineB]]>" in out

    def test_hospital_stage_names(self, builder):
        out = xml(builder.build_from_template("hospital", {"name": "H"}))
        assert "<![CDATA[triage]]>" in out
        assert "<![CDATA[treatment]]>" in out


# ---------------------------------------------------------------------------
# Entity types
# ---------------------------------------------------------------------------

class TestEntityTypes:
    def test_warehouse_entity_is_truck(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "<![CDATA[Truck]]>" in out

    def test_simple_queue_entity_is_customer(self, builder):
        out = xml(builder.build_from_template("simple_queue", {"name": "Q"}))
        assert "<![CDATA[Customer]]>" in out

    def test_factory_entity_is_part(self, builder):
        out = xml(builder.build_from_template("factory", {"name": "F"}))
        assert "<![CDATA[Part]]>" in out

    def test_hospital_entity_is_patient(self, builder):
        out = xml(builder.build_from_template("hospital", {"name": "H"}))
        assert "<![CDATA[Patient]]>" in out


# ---------------------------------------------------------------------------
# TimePlot chart
# ---------------------------------------------------------------------------

class TestTimePlot:
    def test_timeplot_present(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "<TimePlot>" in out

    def test_timeplot_expression_no_root_prefix(self, builder):
        """Chart expressions must NOT have a 'root.' prefix."""
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "root." not in out

    def test_timeplot_queue_size_expression(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "serviceQueue.size()" in out

    def test_timeplot_throughput_expression(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "sink.count()" in out

    def test_factory_has_two_chart_series(self, builder):
        out = xml(builder.build_from_template("factory", {"name": "F"}))
        # Two Delay blocks → two queue-size series
        assert "machineAQueue.size()" in out
        assert "machineBQueue.size()" in out

    def test_expression2_flag_true(self, builder):
        """Expression2Flag=true puts chart in live-value mode."""
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "<Expression2Flag>true</Expression2Flag>" in out


# ---------------------------------------------------------------------------
# Required XML structure
# ---------------------------------------------------------------------------

class TestXMLStructure:
    def test_has_simulation_experiment(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "<SimulationExperiment" in out

    def test_simulation_experiment_has_no_presentation(self, builder):
        """SimulationExperiment must have no <Presentation> block."""
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        exp_start = out.index("<SimulationExperiment")
        exp_end = out.index("</SimulationExperiment>")
        exp_block = out[exp_start:exp_end]
        assert "<Presentation>" not in exp_block

    def test_has_database_element(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "<Database>" in out

    def test_has_required_library_references(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "com.anylogic.libraries.processmodeling" in out
        assert "com.anylogic.libraries.modules.markup_descriptors" in out

    def test_has_converters_applied(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "<ConvertersApplied>" in out

    def test_bypass_initial_screen_true(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "<BypassInitialScreen>true</BypassInitialScreen>" in out

    def test_agent_link_name_is_connections(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "<![CDATA[connections]]>" in out

    def test_model_time_unit_is_minute(self, builder):
        out = xml(builder.build_from_template("warehouse", {"name": "W"}))
        assert "<ModelTimeUnit><![CDATA[Minute]]></ModelTimeUnit>" in out


# ---------------------------------------------------------------------------
# Custom model — params passthrough
# ---------------------------------------------------------------------------

class TestCustomModel:
    def _custom(self, builder, **block_overrides):
        source_params = block_overrides.get("source_params", {"interarrivalTime": "exponential(1.0/10.0)"})
        delay_params = block_overrides.get("delay_params", {"capacity": "3", "delayTime": "triangular(5,10,15)"})
        defn = ModelDefinition(
            name="CustomTest",
            description="Test",
            agent_types=[{"name": "Widget", "blocks": [
                {"type": "Source", "name": "src", "params": source_params},
                {"type": "Delay",  "name": "proc", "params": delay_params},
                {"type": "Sink",   "name": "done", "params": {}},
            ]}]
        )
        return xml(builder.build_model(defn))

    def test_custom_entity_name(self, builder):
        out = self._custom(builder)
        assert "<![CDATA[Widget]]>" in out

    def test_custom_interarrival_time_passes_through(self, builder):
        out = self._custom(builder, source_params={"interarrivalTime": "exponential(1.0/7.0)"})
        assert "1.0/7.0" in out

    def test_custom_delay_capacity_passes_through(self, builder):
        out = self._custom(builder, delay_params={"capacity": "4", "delayTime": "triangular(5,10,15)"})
        assert "<![CDATA[4]]>" in out

    def test_custom_delay_time_passes_through(self, builder):
        out = self._custom(builder, delay_params={"capacity": "1", "delayTime": "triangular(2,8,20)"})
        assert "triangular(2,8,20)" in out

    def test_custom_queue_auto_injected(self, builder):
        out = self._custom(builder)
        assert "<ClassName><![CDATA[Queue]]></ClassName>" in out

    def test_custom_chart_uses_block_names(self, builder):
        out = self._custom(builder)
        assert "procQueue.size()" in out
        assert "done.count()" in out
