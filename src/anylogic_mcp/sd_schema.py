"""Pydantic schema for System Dynamics model definitions."""

from __future__ import annotations

import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from .ple_validator import PLELimits

TimeUnit = Literal["Year", "Month", "Day", "Hour", "Minute", "Second"]

JAVA_KEYWORDS = frozenset({
    "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char",
    "class", "const", "continue", "default", "do", "double", "else", "enum",
    "extends", "false", "final", "finally", "float", "for", "goto", "if",
    "implements", "import", "instanceof", "int", "interface", "long", "native",
    "new", "null", "package", "private", "protected", "public", "return",
    "short", "static", "strictfp", "super", "switch", "synchronized", "this",
    "throw", "throws", "transient", "true", "try", "void", "volatile", "while",
    "Math", "max", "min", "abs", "pow", "sqrt", "exp", "log", "sin", "cos",
    "tan", "floor", "ceil", "round",
})

JAVA_SAFE_NAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
IDENTIFIER_RE = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b")
UNSAFE_FORMULA_PATTERNS = re.compile(
    r"(;|\bnew\b|\bimport\b|\bclass\b|\bRuntime\b|\bSystem\b|\bProcess\b|\bThread\b)",
    re.IGNORECASE,
)


def _validate_java_name(name: str, field_label: str) -> str:
    if not JAVA_SAFE_NAME.match(name):
        raise ValueError(
            f"{field_label} '{name}' is not a valid Java identifier "
            "(use letters, digits, underscore; must not start with a digit)"
        )
    if name in JAVA_KEYWORDS:
        raise ValueError(f"{field_label} '{name}' conflicts with a reserved Java keyword")
    return name


def extract_formula_identifiers(formula: str) -> set[str]:
    """Return identifier tokens referenced in a formula expression."""
    return {m.group(1) for m in IDENTIFIER_RE.finditer(formula)}


def validate_formula_safe(formula: str, context: str) -> None:
    if UNSAFE_FORMULA_PATTERNS.search(formula):
        raise ValueError(
            f"Formula for {context} contains disallowed Java constructs. "
            "Use math expressions with variable names, Math.*, max(), min(), and ternaries only."
        )


class TablePointDef(BaseModel):
    x: float
    y: float


class StockDef(BaseModel):
    name: str
    initial_value: str = Field(description="Numeric literal or expression for initial stock level")
    expression: Optional[str] = Field(
        default=None,
        description="Net rate expression (inflows minus outflows). Auto-derived from flows if omitted.",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return _validate_java_name(v, "Stock")


class FlowDef(BaseModel):
    name: str
    formula: str
    source: Optional[str] = Field(
        default=None,
        description="Source stock name (omit for cloud inflow)",
    )
    target: Optional[str] = Field(
        default=None,
        description="Target stock name (omit for cloud outflow)",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return _validate_java_name(v, "Flow")

    @field_validator("formula")
    @classmethod
    def validate_formula(cls, v: str) -> str:
        validate_formula_safe(v, "flow")
        return v


class AuxDef(BaseModel):
    name: str
    formula: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return _validate_java_name(v, "Auxiliary")

    @field_validator("formula")
    @classmethod
    def validate_formula(cls, v: str) -> str:
        validate_formula_safe(v, "auxiliary")
        return v


class ParameterDef(BaseModel):
    name: str
    default: str
    label: Optional[str] = None
    slider_min: Optional[float] = None
    slider_max: Optional[float] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return _validate_java_name(v, "Parameter")

    @field_validator("default")
    @classmethod
    def validate_default(cls, v: str) -> str:
        validate_formula_safe(v, "parameter default")
        return v


class TableFunctionDef(BaseModel):
    name: str
    points: list[TablePointDef] = Field(min_length=2)
    interpolation: Literal["LINEAR", "STEP"] = "LINEAR"
    out_of_range: Literal["ERROR", "EXTRAPOLATE", "CUSTOM"] = "EXTRAPOLATE"

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return _validate_java_name(v, "TableFunction")


class LinkDef(BaseModel):
    source: str
    target: str

    @field_validator("source", "target")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        return _validate_java_name(v, "Link endpoint")


class ChartSeriesDef(BaseModel):
    title: str
    expression: str


class ChartDef(BaseModel):
    title: str = "Time Plot"
    series: list[ChartSeriesDef] = Field(min_length=1)


class SDModelDefinition(BaseModel):
    """Explicit System Dynamics model contract for AnyLogic .alp generation."""

    name: str
    description: str
    time_unit: TimeUnit = "Year"
    duration: float = Field(gt=0, description="Simulation stop time in model time units")
    stocks: list[StockDef] = Field(default_factory=list)
    flows: list[FlowDef] = Field(default_factory=list)
    auxiliaries: list[AuxDef] = Field(default_factory=list)
    parameters: list[ParameterDef] = Field(default_factory=list)
    table_functions: list[TableFunctionDef] = Field(default_factory=list)
    links: list[LinkDef] = Field(default_factory=list)
    charts: Optional[list[ChartDef]] = None

    @model_validator(mode="after")
    def validate_model(self) -> SDModelDefinition:
        self._check_unique_names()
        self._check_stock_flow_refs()
        self._check_link_endpoints()
        self._check_formula_refs()
        self._check_ple_variable_limit()
        return self

    def all_variable_names(self) -> set[str]:
        names: set[str] = set()
        for coll in (self.stocks, self.flows, self.auxiliaries, self.parameters):
            for item in coll:
                names.add(item.name)
        for tf in self.table_functions:
            names.add(tf.name)
        return names

    def variable_count(self) -> int:
        return (
            len(self.stocks)
            + len(self.flows)
            + len(self.auxiliaries)
            + len(self.parameters)
            + len(self.table_functions)
        )

    def stock_expressions(self) -> dict[str, str]:
        """Resolved net-rate expression per stock."""
        result: dict[str, str] = {}
        for stock in self.stocks:
            if stock.expression:
                result[stock.name] = stock.expression
                continue
            inflows = [f.name for f in self.flows if f.target == stock.name]
            outflows = [f.name for f in self.flows if f.source == stock.name]
            if not inflows and not outflows:
                raise ValueError(
                    f"Stock '{stock.name}' has no expression and no connected flows"
                )
            terms: list[str] = []
            terms.extend(inflows)
            for out in outflows:
                terms.append(f"-{out}" if not out.startswith("-") else out)
            result[stock.name] = " + ".join(terms) if terms else "0"
        return result

    def to_store_dict(self, model_id: str) -> dict:
        return {
            "id": model_id,
            "name": self.name,
            "description": self.description,
            "paradigm": "system_dynamics",
            "uses_process_library": False,
            "time_unit": self.time_unit,
            "duration": self.duration,
            "duration_hours": self._duration_hours(),
            "system_dynamics": {
                "stocks": [s.model_dump() for s in self.stocks],
                "flows": [f.model_dump() for f in self.flows],
                "auxiliaries": [a.model_dump() for a in self.auxiliaries],
                "parameters": [p.model_dump() for p in self.parameters],
                "table_functions": [t.model_dump() for t in self.table_functions],
                "links": [lnk.model_dump() for lnk in self.links],
                "variable_count": self.variable_count(),
            },
        }

    def _duration_hours(self) -> float:
        unit_hours = {
            "Second": 1 / 3600,
            "Minute": 1 / 60,
            "Hour": 1,
            "Day": 24,
            "Month": 24 * 30,
            "Year": 24 * 365,
        }
        return self.duration * unit_hours[self.time_unit]

    def _check_unique_names(self) -> None:
        seen: dict[str, str] = {}
        for kind, items in (
            ("stock", self.stocks),
            ("flow", self.flows),
            ("auxiliary", self.auxiliaries),
            ("parameter", self.parameters),
            ("table_function", self.table_functions),
        ):
            for item in items:
                if item.name in seen:
                    raise ValueError(
                        f"Duplicate name '{item.name}' used as both {seen[item.name]} and {kind}"
                    )
                seen[item.name] = kind

    def _check_stock_flow_refs(self) -> None:
        stock_names = {s.name for s in self.stocks}
        for flow in self.flows:
            if flow.source and flow.source not in stock_names:
                raise ValueError(
                    f"Flow '{flow.name}' source '{flow.source}' is not a defined stock"
                )
            if flow.target and flow.target not in stock_names:
                raise ValueError(
                    f"Flow '{flow.name}' target '{flow.target}' is not a defined stock"
                )
            if not flow.source and not flow.target:
                raise ValueError(
                    f"Flow '{flow.name}' must have at least one of source or target"
                )

    def _check_link_endpoints(self) -> None:
        known = self.all_variable_names()
        for link in self.links:
            if link.source not in known:
                raise ValueError(
                    f"Link source '{link.source}' is not a defined variable"
                )
            if link.target not in known:
                raise ValueError(
                    f"Link target '{link.target}' is not a defined variable"
                )

    def _check_formula_refs(self) -> None:
        known = self.all_variable_names()
        for flow in self.flows:
            self._check_formula_identifiers(flow.formula, flow.name, known)
        for aux in self.auxiliaries:
            self._check_formula_identifiers(aux.formula, aux.name, known, allow_self=False)
        for stock in self.stocks:
            expr = stock.expression or ""
            if expr:
                self._check_formula_identifiers(expr, stock.name, known, allow_self=False)
        for param in self.parameters:
            self._check_formula_identifiers(param.default, param.name, known, allow_self=False)

    def _check_formula_identifiers(
        self,
        formula: str,
        owner: str,
        known: set[str],
        allow_self: bool = True,
    ) -> None:
        for ident in extract_formula_identifiers(formula):
            if ident in JAVA_KEYWORDS:
                continue
            if not allow_self and ident == owner:
                continue
            if ident not in known:
                raise ValueError(
                    f"Formula for '{owner}' references unknown identifier '{ident}'. "
                    f"Known variables: {sorted(known)}"
                )

    def _check_ple_variable_limit(self) -> None:
        count = self.variable_count()
        if count > PLELimits.MAX_SYSTEM_DYNAMICS_VARS:
            raise ValueError(
                f"Too many system dynamics variables: {count} "
                f"(PLE limit: {PLELimits.MAX_SYSTEM_DYNAMICS_VARS})"
            )
