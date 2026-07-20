"""Acceptance tests for Food Security Malaysia SD model (Bala et al., Ch. 10)."""

from anylogic_mcp.sd_builder import SDModelBuilder
from anylogic_mcp.sd_templates import build_template
from anylogic_mcp.sd_validator import SDValidator
from anylogic_mcp.ple_validator import PLEValidator


def test_food_security_stock_names():
    model = build_template("food_security_malaysia", {})
    stock_names = {s.name for s in model.stocks}
    expected = {
        "riceArea",
        "croppingIntensity",
        "riceProductivityPotential",
        "landDegradationMultiplier",
        "trainingExtensionMultiplier",
        "learning",
        "trainingAndExtension",
        "bioFertilizerFraction",
        "population",
    }
    assert expected.issubset(stock_names)


def test_food_security_ssl_auxiliary():
    model = build_template("food_security_malaysia", {})
    aux_names = {a.name for a in model.auxiliaries}
    assert "selfSufficiencyLevel" in aux_names
    assert "riceProduction" in aux_names
    assert "riceRequirement" in aux_names


def test_food_security_time_and_duration():
    model = build_template("food_security_malaysia", {})
    assert model.time_unit == "Year"
    assert model.duration == 50


def test_food_security_variable_count_within_ple():
    model = build_template("food_security_malaysia", {})
    assert model.variable_count() <= 200


def test_food_security_generates_openable_xml():
    model = build_template("food_security_malaysia", {})
    data = SDModelBuilder().build_model(model)
    text = data.decode("utf-8")
    assert "selfSufficiencyLevel" in text
    assert "riceArea" in text
    assert 'Class="StockVariable"' in text


def test_food_security_passes_validators():
    model = build_template("food_security_malaysia", {})
    store = model.to_store_dict("fs-id")
    assert SDValidator().validate(model).is_valid
    assert PLEValidator().validate_model(store).is_valid
