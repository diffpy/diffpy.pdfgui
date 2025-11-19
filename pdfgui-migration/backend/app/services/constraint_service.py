"""Constraint service - wraps pdfGUI constraint handling.

Wraps: diffpy.pdfgui.control.constraint
"""

import math
from typing import Any, Dict, List, Optional

from diffpy.pdfgui.control.constraint import Constraint
from diffpy.pdfgui.control.controlerrors import ControlSyntaxError


class ConstraintService:
    """Service for parameter constraint operations."""

    def create_constraint(self, formula: str) -> Dict[str, Any]:
        """Create and validate a constraint.

        Wraps: Constraint.__init__()
        Validates syntax and parses formula.
        """
        try:
            constraint = Constraint(formula)
            return {"formula": formula, "parameters": constraint.parguess(), "valid": True, "error": None}
        except ControlSyntaxError as e:
            return {"formula": formula, "parameters": [], "valid": False, "error": str(e)}

    def validate_formula(self, formula: str) -> Dict[str, Any]:
        """Validate constraint formula syntax.

        Wraps: Constraint formula validation
        """
        try:
            constraint = Constraint(formula)
            return {"valid": True, "parameters": constraint.parguess(), "error": None}
        except ControlSyntaxError as e:
            return {"valid": False, "parameters": [], "error": str(e)}

    def evaluate_formula(self, formula: str, parameter_values: Dict[int, float]) -> Dict[str, Any]:
        """Evaluate constraint formula with parameter values.

        Wraps: Constraint.evalFormula()
        """
        try:
            constraint = Constraint(formula)
            value = constraint.evalFormula(parameter_values)
            return {"value": float(value), "error": None}
        except Exception as e:
            return {"value": None, "error": str(e)}

    def get_parameters_used(self, formula: str) -> List[int]:
        """Get list of parameter indices used in formula.

        Wraps: Constraint.parguess()
        """
        try:
            constraint = Constraint(formula)
            return constraint.parguess()
        except:
            return []

    def transform_formula(self, formula: str, index_map: Dict[int, int]) -> str:
        """Transform parameter indices in formula.

        Used when parameters are renumbered.
        """
        import re

        def replace_param(match):
            old_idx = int(match.group(1))
            new_idx = index_map.get(old_idx, old_idx)
            return f"@{new_idx}"

        return re.sub(r"@(\d+)", replace_param, formula)

    def get_standard_functions(self) -> List[Dict[str, str]]:
        """Get list of supported mathematical functions.

        These are the functions supported in constraint formulas.
        """
        return [
            {"name": "sin", "description": "Sine function"},
            {"name": "cos", "description": "Cosine function"},
            {"name": "tan", "description": "Tangent function"},
            {"name": "asin", "description": "Arc sine"},
            {"name": "acos", "description": "Arc cosine"},
            {"name": "atan", "description": "Arc tangent"},
            {"name": "exp", "description": "Exponential"},
            {"name": "log", "description": "Natural logarithm"},
            {"name": "log10", "description": "Base-10 logarithm"},
            {"name": "sqrt", "description": "Square root"},
            {"name": "abs", "description": "Absolute value"},
        ]

    def build_constraint_set(self, constraints: List[Dict[str, str]]) -> Dict[str, Constraint]:
        """Build a set of constraints from definitions.

        Args:
            constraints: List of {"target": ..., "formula": ...}

        Returns:
            Dictionary mapping target to Constraint object
        """
        result = {}
        for c in constraints:
            target = c["target"]
            formula = c["formula"]
            result[target] = Constraint(formula)
        return result

    def check_circular_dependencies(self, constraints: Dict[str, str]) -> Dict[str, Any]:
        """Check for circular dependencies in constraints.

        Returns error if circular dependency detected.
        """
        # Build dependency graph
        deps = {}
        for target, formula in constraints.items():
            params = self.get_parameters_used(formula)
            deps[target] = params

        # Check for cycles (simplified check)
        visited = set()
        for target in deps:
            if target in visited:
                continue

            path = [target]
            current = target

            while True:
                params = deps.get(current, [])
                if not params:
                    break

                # Check if any parameter creates a cycle
                for param in params:
                    param_key = f"@{param}"
                    if param_key in path:
                        return {"has_cycle": True, "cycle": path + [param_key]}

                visited.add(current)
                break

        return {"has_cycle": False, "cycle": []}
