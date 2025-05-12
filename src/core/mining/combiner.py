# /src/core/mining/combiner.py

"""Constraint combiner for merging static and dynamic constraints."""

import uuid
import re
from typing import Dict, List, Tuple
from schemas.constraint import StaticConstraint, DynamicInvariant, UnifiedConstraint


class ConstraintCombiner:
    """
    Core component for combining static constraints and dynamic invariants.

    When constraints overlap, chooses the stricter of the two or merges them
    when they provide complementary information.
    """

    def combine_constraints(
        self,
        static_constraints: List[StaticConstraint],
        dynamic_invariants: List[DynamicInvariant],
    ) -> List[UnifiedConstraint]:
        """
        Combine static constraints and dynamic invariants into unified constraints.

        Args:
            static_constraints: List of static constraints from API specification
            dynamic_invariants: List of dynamic invariants from execution logs

        Returns:
            List of unified constraints
        """
        unified_constraints = []

        # Start by adding all static constraints
        for constraint in static_constraints:
            unified = UnifiedConstraint(
                id=f"unified-{uuid.uuid4()}",
                expression=constraint.expression,
                originating_ids=[constraint.id],
            )
            unified_constraints.append(unified)

        # Process dynamic invariants
        for invariant in dynamic_invariants:
            matching = self._find_matching_constraints(invariant, unified_constraints)

            if matching:
                # For each match, decide whether to update, merge or leave as-is
                for match in matching:
                    merged = self._merge_constraints(match, invariant)
                    if merged and merged != match:
                        # Update with merged version
                        idx = unified_constraints.index(match)
                        unified_constraints[idx] = merged
            else:
                # Add as new constraint
                unified = UnifiedConstraint(
                    id=f"unified-{uuid.uuid4()}",
                    expression=invariant.expression,
                    originating_ids=[invariant.id],
                )
                unified_constraints.append(unified)

        return unified_constraints

    def _find_matching_constraints(
        self, invariant: DynamicInvariant, unified_constraints: List[UnifiedConstraint]
    ) -> List[UnifiedConstraint]:
        """Find unified constraints that target the same variables as an invariant."""
        matches = []

        for constraint in unified_constraints:
            # Simple string matching for demo - would be more sophisticated in real impl
            if self._constraints_overlap(constraint.expression, invariant.expression):
                matches.append(constraint)

        return matches

    def _constraints_overlap(self, expr1: str, expr2: str) -> bool:
        """Check if two constraint expressions reference the same variables."""
        # Simple heuristic: check if both expressions reference the same property

        # Extract property names from expressions
        props1 = re.findall(r"response\.([a-zA-Z0-9_\.]+)", expr1)
        props2 = re.findall(r"response\.([a-zA-Z0-9_\.]+)", expr2)

        # Look for overlap
        return any(p1 == p2 for p1 in props1 for p2 in props2)

    def _merge_constraints(
        self, unified: UnifiedConstraint, invariant: DynamicInvariant
    ) -> UnifiedConstraint:
        """Merge a dynamic invariant into an existing unified constraint."""
        # Determine which constraint is stricter
        stricter_expr = self._select_stricter_constraint(
            unified.expression, invariant.expression
        )

        if stricter_expr == unified.expression:
            # No change needed
            return unified

        # Create new merged constraint with stricter expression
        return UnifiedConstraint(
            id=unified.id,  # Keep same ID
            expression=stricter_expr,
            originating_ids=unified.originating_ids + [invariant.id],
        )

    def _select_stricter_constraint(self, expr1: str, expr2: str) -> str:
        """Select the stricter of two constraint expressions."""
        # This is a simplified version for demo
        # In a real implementation, this would use more sophisticated analysis,
        # possibly with an LLM to compare the constraints

        # Look for inequality comparisons
        ineq1 = re.search(r"([<>]=?)\s*(\d+)", expr1)
        ineq2 = re.search(r"([<>]=?)\s*(\d+)", expr2)

        if not ineq1 or not ineq2:
            # Can't compare, return first
            return expr1

        op1, val1 = ineq1.groups()
        op2, val2 = ineq2.groups()
        val1, val2 = int(val1), int(val2)

        # Handle greater-than style
        if ">" in op1 and ">" in op2:
            return expr1 if val1 > val2 else expr2

        # Handle less-than style
        if "<" in op1 and "<" in op2:
            return expr1 if val1 < val2 else expr2

        # Mixed comparison types - default to first
        return expr1
