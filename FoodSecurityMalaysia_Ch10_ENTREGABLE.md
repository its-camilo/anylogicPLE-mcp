# Food Security Malaysia - Modelo SD Completo (Cap. 10)

## Conteo de Variables

| Tipo | Cantidad |
|------|----------|
| Stocks | 10 |
| Flows | 11 |
| Auxiliaries | 8 |
| Parameters | 9 |
| Table Functions | 5 |
| **Total** | **43 / 200** |

---

## Ecuaciones 10.1-10.13 Implementadas

| Ec. | Formula implementada |
|-----|---------------------|
| 10.1 | riceProduction = riceProductivity * riceArea * croppingIntensity |
| 10.2 | stock riceArea; inflow=availableLand/8; outflow=riceArea*0.0085 |
| 10.3 | stock croppingIntensity; inflow=(croppingIntensityTarget-croppingIntensity)/50 |
| 10.4 | riceProductivity = potential * fromInput * fromLandDeg * fromTraining |
| 10.5 | stock riceProductivityPotential; inflow=rdFundingEnabled*(target-potential)/50 |
| 10.6 | stock riceProductivityMultFromLandDeg; inflow=regeneration; outflow=degenerationRate |
| 10.7 | stock productivityMultFromTrainingExt; inflow=productivityIncreaseFromLearning |
| 10.8 | stock learning; inflow=learningFromExtensionTable(trainingAndExtension)*(1-learning) |
| 10.9 | stock trainingAndExtension; inflow=(extensionCoverageTarget-trainingAndExtension)/50 |
| 10.10 | stock bioFertilizerFraction; inflow=(bioFertFractionTarget-bioFert)/bioFertTransitionYears |
| 10.11 | riceRequirement = perCapitaRiceConsumption * population * ricePaddyConversionFactor |
| 10.12 | stock population; inflow=population*0.021 |
| 10.13 | selfSufficiencyLevel = riceProduction / max(1, riceRequirement) |

---

## Parametros (Table 10.1)

| Variable | Valor | Unidad |
|----------|-------|--------|
| riceArea | 680647 | ha |
| availableLand | 88000 | ha |
| conversionTime | 8 | years |
| discardRate | 0.0085 | per year |
| population | 18.1024 | million |
| populationGrowth | 0.021 | fraction/year |
| perCapitaRiceConsumption | 0.08 | t/person/year |
| riceProductivityPotential | 6.0 | t/ha |
| riceProductivityMultFromLandDeg | 0.99 | dimensionless |
| productivityMultFromTrainingExt | 0.61 | dimensionless |
| bioFertilizerFraction | 0.0 | fraction |

---

## Presets Escenarios S1-S7

| ID | Subsidy | BioFert | RD | ProdTarget | Extension | CI_mult | SSL yr50 | Prod yr50 |
|----|---------|---------|----|----|-----------|---------|----------|-----------|
| S1 | 0.67 | 0.0 | 0 | 6 | 0 | 1.0 | 22% | 1.54 Mt |
| S2 | 0.0 | 0.0 | 0 | 6 | 0 | 1.0 | 19% | 1.33 Mt |
| S3 | 0.0 | 0.5 | 0 | 6 | 0 | 1.0 | 21% | 1.42 Mt |
| S4 | 0.0 | 0.5 | 1 | 12 | 0 | 1.0 | 35% | 2.42 Mt |
| S5 | 0.0 | 0.5 | 1 | 12 | 1 | 1.0 | 43% | 2.99 Mt |
| S6 | 0.0 | 0.5 | 1 | 12 | 1 | 1.5 | 63% | 4.34 Mt |
| S7 | 0.67 | 0.0 | 0 | 2.5/3.5/4.5 | 0 | 1.0 | Fig10.4 | - |

---

## Table Functions

| Nombre | Eje X | Eje Y | Relacion |
|--------|-------|-------|---------|
| productivityFromInputTable | input ratio 0-1.5 | efecto 0-0.65 | insumos->productividad |
| degradationFactorTable | croppingIntensity 0.5-3 | tasa 0.001-0.04 | intensidad->degradacion |
| regenerationFactorTable | mult landDeg 0.5-1 | tasa 0-0.05 | auto-regeneracion suelo |
| learningFromExtensionTable | cobertura 0-1 | tasa 0-0.08 | extension->aprendizaje FFS |
| productivityFromLearningTable | aprendizaje 0-1 | aumento 0-0.02 | aprendizaje->brecha productividad |

---

## Como Correr Escenarios en AnyLogic PLE

1. Abrir FoodSecurityMalaysia_Ch10.alp en AnyLogic PLE 8.9.x
2. Clic Run -> panel Parameters a la izquierda
3. Ajustar sliders segun tabla S1-S7 arriba
4. Observar graficos: SSL (%), Rice Production vs Requirement, Rice Area

**S1**: inputSubsidyFraction=0.67, todo lo demas en default
**S2**: inputSubsidyFraction=0
**S3**: inputSubsidyFraction=0, bioFertFractionTarget=0.5
**S4**: S3 + rdFundingEnabled=1, productivityPotentialTarget=12
**S5**: S4 + extensionCoverageTarget=1
**S6**: S5 + croppingIntensityMultiplier=1.5
**S7**: S1 + variar productivityPotentialTarget = 2.5, 3.5, 4.5

---

## Archivo

Ruta: C:/Users/camil/Documents/Simulations/FoodSecurityMalaysia_Ch10.alp
Model ID MCP: 02803969-d13a-40d0-9a6d-8e513efbac39
Variables: 43/200