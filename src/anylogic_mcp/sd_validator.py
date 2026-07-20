"""Semantic validation for System Dynamics model definitions."""

from __future__ import annotations

from dataclasses import dataclass, field

from .sd_schema import SDModelDefinition, extract_formula_identifiers


@dataclass
class SDValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }


class SDValidator:
    """Additional semantic checks beyond Pydantic schema validation."""

    def validate(self, model: SDModelDefinition) -> SDValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        stock_exprs = model.stock_expressions()
        self._check_stock_flow_consistency(model, stock_exprs, errors)
        self._check_link_coverage(model, warnings)
        self._check_duration_warning(model, warnings)

        return SDValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _check_stock_flow_consistency(
        self,
        model: SDModelDefinition,
        stock_exprs: dict[str, str],
        errors: list[str],
    ) -> None:
        for stock in model.stocks:
            if not stock.expression:
                continue
            inflows = {f.name for f in model.flows if f.target == stock.name}
            outflows = {f.name for f in model.flows if f.source == stock.name}
            expr_idents = extract_formula_identifiers(stock.expression)
            flow_refs = inflows | outflows
            missing = flow_refs - expr_idents
            if missing:
                errors.append(
                    f"Stock '{stock.name}' expression does not reference connected flows: "
                    f"{sorted(missing)}"
                )

    def _check_link_coverage(
        self,
        model: SDModelDefinition,
        warnings: list[str],
    ) -> None:
        linked = {(lnk.source, lnk.target) for lnk in model.links}
        known = model.all_variable_names()

        for flow in model.flows:
            refs = extract_formula_identifiers(flow.formula) & known
            for ref in refs:
                if ref == flow.name:
                    continue
                if (ref, flow.name) not in linked and (flow.name, ref) not in linked:
                    warnings.append(
                        f"Flow '{flow.name}' uses '{ref}' but no causal link is declared "
                        f"between them"
                    )

        for aux in model.auxiliaries:
            refs = extract_formula_identifiers(aux.formula) & known
            for ref in refs:
                if ref == aux.name:
                    continue
                if (ref, aux.name) not in linked and (aux.name, ref) not in linked:
                    warnings.append(
                        f"Auxiliary '{aux.name}' uses '{ref}' but no causal link is declared "
                        f"between them"
                    )

    def _check_duration_warning(
        self,
        model: SDModelDefinition,
        warnings: list[str],
    ) -> None:
        hours = model._duration_hours()
        if hours > 5:
            warnings.append(
                f"Simulation duration (~{hours:.0f} wall-clock hours at 1:1 speed) may exceed "
                "PLE's 5-hour limit for non-Process-Library models. "
                "Use faster animation or shorter duration for long horizons."
            )
