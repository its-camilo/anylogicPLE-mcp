"""Built-in System Dynamics model templates."""

from __future__ import annotations

from typing import Any, Optional

from .sd_schema import (
    AuxDef,
    ChartDef,
    ChartSeriesDef,
    FlowDef,
    LinkDef,
    ParameterDef,
    SDModelDefinition,
    StockDef,
    TableFunctionDef,
    TablePointDef,
)


def build_template(template_name: str, params: Optional[dict[str, Any]] = None) -> SDModelDefinition:
    params = params or {}
    builders = {
        "predator_prey": _predator_prey,
        "simple_stock_flow": _simple_stock_flow,
        "food_security_malaysia": _food_security_malaysia,
    }
    fn = builders.get(template_name)
    if fn is None:
        raise ValueError(
            f"Unknown SD template: {template_name}. "
            f"Available: {', '.join(sorted(builders))}"
        )
    return fn(params)


def _predator_prey(params: dict[str, Any]) -> SDModelDefinition:
    name = params.get("name", "Predator Prey")
    description = params.get(
        "description",
        "Classical predator-prey dynamics (lynx and hares)",
    )
    return SDModelDefinition(
        name=name,
        description=description,
        time_unit="Year",
        duration=float(params.get("duration", 100)),
        parameters=[
            ParameterDef(name="Area", default="100", label="Area", slider_min=20, slider_max=500),
            ParameterDef(
                name="HareNatality",
                default="1.25",
                label="Hare natality",
                slider_min=0.25,
                slider_max=3.0,
            ),
            ParameterDef(
                name="LynxNatality",
                default="0.25",
                label="Lynx natality",
                slider_min=0.1,
                slider_max=0.5,
            ),
        ],
        stocks=[
            StockDef(name="Hares", initial_value="6000", expression="HareBirths - HareDeaths"),
            StockDef(name="Lynx", initial_value="125", expression="LynxBirths - LynxDeaths"),
        ],
        flows=[
            FlowDef(
                name="HareBirths",
                formula="Math.max(Hares, 0) * HareNatality",
                target="Hares",
            ),
            FlowDef(
                name="HareDeaths",
                formula="HareDensity * Lynx",
                source="Hares",
            ),
            FlowDef(
                name="LynxBirths",
                formula="Lynx * LynxNatality",
                target="Lynx",
            ),
            FlowDef(
                name="LynxDeaths",
                formula="Lynx * LynxMortality(HareDensity)",
                source="Lynx",
            ),
        ],
        auxiliaries=[
            AuxDef(name="HareDensity", formula="Hares / Area"),
        ],
        table_functions=[
            TableFunctionDef(
                name="LynxMortality",
                points=[
                    TablePointDef(x=0, y=0.5),
                    TablePointDef(x=20, y=0.4),
                    TablePointDef(x=40, y=0.3),
                    TablePointDef(x=60, y=0.2),
                    TablePointDef(x=80, y=0.1),
                ],
            ),
        ],
        links=[
            LinkDef(source="Hares", target="HareBirths"),
            LinkDef(source="HareNatality", target="HareBirths"),
            LinkDef(source="Hares", target="HareDeaths"),
            LinkDef(source="HareDensity", target="HareDeaths"),
            LinkDef(source="Lynx", target="HareDeaths"),
            LinkDef(source="Lynx", target="LynxBirths"),
            LinkDef(source="LynxNatality", target="LynxBirths"),
            LinkDef(source="Lynx", target="LynxDeaths"),
            LinkDef(source="HareDensity", target="LynxDeaths"),
            LinkDef(source="Hares", target="HareDensity"),
            LinkDef(source="Area", target="HareDensity"),
        ],
        charts=[
            ChartDef(
                title="Populations",
                series=[
                    ChartSeriesDef(title="Hares", expression="Hares"),
                    ChartSeriesDef(title="Lynx", expression="Lynx"),
                ],
            ),
        ],
    )


def _simple_stock_flow(params: dict[str, Any]) -> SDModelDefinition:
    name = params.get("name", "Simple Stock Flow")
    description = params.get("description", "Single-stock inventory with inflow and outflow")
    return SDModelDefinition(
        name=name,
        description=description,
        time_unit="Month",
        duration=float(params.get("duration", 60)),
        parameters=[
            ParameterDef(name="restockRate", default="50"),
            ParameterDef(name="demandRate", default="40"),
        ],
        stocks=[
            StockDef(
                name="Inventory",
                initial_value="200",
                expression="restocking - sales",
            ),
        ],
        flows=[
            FlowDef(name="restocking", formula="restockRate", target="Inventory"),
            FlowDef(name="sales", formula="demandRate", source="Inventory"),
        ],
        links=[
            LinkDef(source="restockRate", target="restocking"),
            LinkDef(source="restocking", target="Inventory"),
            LinkDef(source="demandRate", target="sales"),
            LinkDef(source="Inventory", target="sales"),
        ],
        charts=[
            ChartDef(
                title="Inventory",
                series=[ChartSeriesDef(title="Inventory", expression="Inventory")],
            ),
        ],
    )


def _food_security_malaysia(params: dict[str, Any]) -> SDModelDefinition:
    """Cap. 10 food security model (Bala et al.) — rice production and SSL in Malaysia."""
    name = params.get("name", "Food Security Malaysia")
    description = params.get(
        "description",
        "System dynamics model of rice food security in Malaysia (Bala et al., Ch. 10)",
    )
    return SDModelDefinition(
        name=name,
        description=description,
        time_unit="Year",
        duration=float(params.get("duration", 50)),
        parameters=[
            ParameterDef(name="availableLand", default="88000"),
            ParameterDef(name="conversionTime", default="8"),
            ParameterDef(name="discardRate", default="0.0085"),
            ParameterDef(name="populationGrowthFraction", default="0.021"),
            ParameterDef(name="perCapitaRiceConsumption", default="80"),
            ParameterDef(name="productivityNormalIncreaseRate", default="0.02"),
            ParameterDef(name="degenerationRate", default="0.005"),
            ParameterDef(name="regenerationFactor", default="0.01"),
            ParameterDef(name="learningIncreaseRate", default="0.05"),
            ParameterDef(name="trainingExtensionIncreaseRate", default="0.03"),
            ParameterDef(name="bioFertilizerGrowthRate", default="0.02"),
            ParameterDef(name="croppingIntensityTarget", default="2.0"),
            ParameterDef(name="croppingIntensityAdjustmentTime", default="5"),
            ParameterDef(name="inputSubsidyRate", default="0.5"),
            ParameterDef(name="recommendedInput", default="1.0"),
            ParameterDef(name="ricePaddyConversionFactor", default="0.65"),
        ],
        stocks=[
            StockDef(name="riceArea", initial_value="680647"),
            StockDef(name="croppingIntensity", initial_value="1.8"),
            StockDef(name="riceProductivityPotential", initial_value="6"),
            StockDef(
                name="landDegradationMultiplier",
                initial_value="0.99",
                expression="regeneration - degeneration",
            ),
            StockDef(
                name="trainingExtensionMultiplier",
                initial_value="0.61",
                expression="productivityIncreaseFromLearning",
            ),
            StockDef(name="learning", initial_value="0.1", expression="learningIncrease"),
            StockDef(
                name="trainingAndExtension",
                initial_value="0.5",
                expression="trainingExtensionIncrease",
            ),
            StockDef(
                name="bioFertilizerFraction",
                initial_value="0.0",
                expression="bioFertilizerGrowth",
            ),
            StockDef(
                name="population",
                initial_value="18.1024",
                expression="populationGrowth",
            ),
        ],
        flows=[
            FlowDef(
                name="riceAreaIncrease",
                formula="Math.max(0, (desiredRiceArea - riceArea) / conversionTime)",
                target="riceArea",
            ),
            FlowDef(
                name="riceAreaDiscard",
                formula="riceArea * discardRate",
                source="riceArea",
            ),
            FlowDef(
                name="croppingIntensityIncrease",
                formula=(
                    "Math.max(0, (croppingIntensityTarget - croppingIntensity) "
                    "/ croppingIntensityAdjustmentTime)"
                ),
                target="croppingIntensity",
            ),
            FlowDef(
                name="productivityPotentialIncrease",
                formula="productivityNormalIncreaseRate",
                target="riceProductivityPotential",
            ),
            FlowDef(
                name="regeneration",
                formula="regenerationFactor * (1 - landDegradationMultiplier)",
                target="landDegradationMultiplier",
            ),
            FlowDef(
                name="degeneration",
                formula="degenerationRate * croppingIntensity",
                source="landDegradationMultiplier",
            ),
            FlowDef(
                name="productivityIncreaseFromLearning",
                formula="learningFractionFromExtension(learning) * 0.1",
                target="trainingExtensionMultiplier",
            ),
            FlowDef(
                name="learningIncrease",
                formula="learningIncreaseRate * trainingAndExtension",
                target="learning",
            ),
            FlowDef(
                name="trainingExtensionIncrease",
                formula="trainingExtensionIncreaseRate",
                target="trainingAndExtension",
            ),
            FlowDef(
                name="bioFertilizerGrowth",
                formula="bioFertilizerGrowthRate * (1 - bioFertilizerFraction)",
                target="bioFertilizerFraction",
            ),
            FlowDef(
                name="populationGrowth",
                formula="population * populationGrowthFraction",
                target="population",
            ),
        ],
        auxiliaries=[
            AuxDef(
                name="desiredRiceArea",
                formula="riceArea + availableLand / conversionTime",
            ),
            AuxDef(
                name="productivityFromInput",
                formula=(
                    "inputSubsidyRate * recommendedInput * (1 - 0.3 * bioFertilizerFraction)"
                ),
            ),
            AuxDef(
                name="riceProductivity",
                formula=(
                    "riceProductivityPotential * productivityFromInput "
                    "* landDegradationMultiplier * trainingExtensionMultiplier"
                ),
            ),
            AuxDef(
                name="riceProduction",
                formula="riceProductivity * riceArea * croppingIntensity * ricePaddyConversionFactor",
            ),
            AuxDef(
                name="riceRequirement",
                formula="perCapitaRiceConsumption * population * 1000",
            ),
            AuxDef(
                name="selfSufficiencyLevel",
                formula="riceProduction / Math.max(riceRequirement, 1)",
            ),
        ],
        table_functions=[
            TableFunctionDef(
                name="learningFractionFromExtension",
                points=[
                    TablePointDef(x=0.0, y=0.0),
                    TablePointDef(x=0.2, y=0.1),
                    TablePointDef(x=0.4, y=0.3),
                    TablePointDef(x=0.6, y=0.5),
                    TablePointDef(x=0.8, y=0.7),
                    TablePointDef(x=1.0, y=0.9),
                ],
            ),
        ],
        links=[
            LinkDef(source="riceArea", target="riceAreaIncrease"),
            LinkDef(source="desiredRiceArea", target="riceAreaIncrease"),
            LinkDef(source="conversionTime", target="riceAreaIncrease"),
            LinkDef(source="riceArea", target="riceAreaDiscard"),
            LinkDef(source="discardRate", target="riceAreaDiscard"),
            LinkDef(source="croppingIntensity", target="croppingIntensityIncrease"),
            LinkDef(source="croppingIntensityTarget", target="croppingIntensityIncrease"),
            LinkDef(source="riceProductivityPotential", target="productivityPotentialIncrease"),
            LinkDef(source="landDegradationMultiplier", target="regeneration"),
            LinkDef(source="regenerationFactor", target="regeneration"),
            LinkDef(source="landDegradationMultiplier", target="degeneration"),
            LinkDef(source="croppingIntensity", target="degeneration"),
            LinkDef(source="degenerationRate", target="degeneration"),
            LinkDef(source="learning", target="productivityIncreaseFromLearning"),
            LinkDef(source="trainingAndExtension", target="learningIncrease"),
            LinkDef(source="learningIncreaseRate", target="learningIncrease"),
            LinkDef(source="trainingExtensionIncreaseRate", target="trainingExtensionIncrease"),
            LinkDef(source="bioFertilizerFraction", target="bioFertilizerGrowth"),
            LinkDef(source="bioFertilizerGrowthRate", target="bioFertilizerGrowth"),
            LinkDef(source="population", target="populationGrowth"),
            LinkDef(source="populationGrowthFraction", target="populationGrowth"),
            LinkDef(source="riceProductivity", target="riceProduction"),
            LinkDef(source="riceArea", target="riceProduction"),
            LinkDef(source="croppingIntensity", target="riceProduction"),
            LinkDef(source="riceProduction", target="selfSufficiencyLevel"),
            LinkDef(source="riceRequirement", target="selfSufficiencyLevel"),
            LinkDef(source="perCapitaRiceConsumption", target="riceRequirement"),
            LinkDef(source="population", target="riceRequirement"),
            LinkDef(source="riceProductivityPotential", target="riceProductivity"),
            LinkDef(source="productivityFromInput", target="riceProductivity"),
            LinkDef(source="landDegradationMultiplier", target="riceProductivity"),
            LinkDef(source="trainingExtensionMultiplier", target="riceProductivity"),
            LinkDef(source="inputSubsidyRate", target="productivityFromInput"),
            LinkDef(source="bioFertilizerFraction", target="productivityFromInput"),
            LinkDef(source="availableLand", target="desiredRiceArea"),
            LinkDef(source="riceArea", target="desiredRiceArea"),
        ],
        charts=[
            ChartDef(
                title="Food Security",
                series=[
                    ChartSeriesDef(title="SSL", expression="selfSufficiencyLevel"),
                    ChartSeriesDef(title="Rice Production", expression="riceProduction"),
                    ChartSeriesDef(title="Rice Requirement", expression="riceRequirement"),
                    ChartSeriesDef(title="Population", expression="population"),
                ],
            ),
        ],
    )
