"""
CVXPY convex optimization models for mathematical programming problems.
"""

from enum import Enum
from typing import Any, Optional, List, Dict, Union

from pydantic import BaseModel, Field

from ..core.base_models import BaseVariable, BaseConstraint, BaseProblem, BaseSolution
from ..core.problem_types import ProblemType, OptimizationSense, VariableType, ConstraintType


class ObjectiveType(str, Enum):
    """Enum for objective types in CVXPY."""

    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


class CVXPYVariable(BaseVariable):
    """Model representing a CVXPY variable."""

    name: str = Field(..., description="Variable name")
    shape: Union[int, tuple[int, ...]] = Field(..., description="Variable shape (scalar or array)")
    description: str = Field(default="", description="Variable description")
    
    # CVXPY-specific properties
    var_type: VariableType = Field(default=VariableType.REAL, description="Variable type")
    nonneg: bool = Field(default=False, description="Non-negative constraint")
    nonpos: bool = Field(default=False, description="Non-positive constraint")
    symmetric: bool = Field(default=False, description="Symmetric matrix constraint")
    diag: bool = Field(default=False, description="Diagonal matrix constraint")
    hermitian: bool = Field(default=False, description="Hermitian matrix constraint")
    complex: bool = Field(default=False, description="Complex variable")
    
    # Bounds
    lower_bound: Optional[float] = Field(default=None, description="Lower bound")
    upper_bound: Optional[float] = Field(default=None, description="Upper bound")

    def get_bounds(self) -> tuple[Optional[float], Optional[float]]:
        """Get variable bounds (lower, upper)."""
        return self.lower_bound, self.upper_bound


class CVXPYConstraint(BaseConstraint):
    """Model representing a CVXPY constraint."""

    expression: str = Field(..., description="Constraint expression as string")
    description: str = Field(default="", description="Constraint description")
    
    # CVXPY-specific properties
    constraint_type: ConstraintType = Field(default=ConstraintType.LINEAR_INEQUALITY, description="Type of constraint")
    is_equality: bool = Field(default=False, description="Whether constraint is equality")
    is_inequality: bool = Field(default=True, description="Whether constraint is inequality")

    def is_linear(self) -> bool:
        """Check if constraint is linear."""
        # Simple heuristic - CVXPY constraints are typically linear
        # unless they involve non-linear functions
        non_linear_indicators = ["**", "^", "sqrt", "log", "exp", "sin", "cos", "quad_form", "norm"]
        expr_lower = self.expression.lower()
        return not any(indicator in expr_lower for indicator in non_linear_indicators)


class CVXPYObjective(BaseModel):
    """Model representing a CVXPY objective."""

    type: ObjectiveType = Field(..., description="Objective type")
    expression: str = Field(..., description="Objective function expression as string")
    description: str = Field(default="", description="Objective description")


class CVXPYProblem(BaseProblem):
    """Model representing a complete CVXPY optimization problem."""

    variables: List[CVXPYVariable] = Field(..., description="Problem variables")
    objective: CVXPYObjective = Field(..., description="Problem objective")
    constraints: List[CVXPYConstraint] = Field(..., description="Problem constraints")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Problem parameters")
    description: str = Field(default="", description="Problem description")
    
    # CVXPY-specific properties
    problem_type: ProblemType = Field(default=ProblemType.CONVEX_OPTIMIZATION, description="Problem type")
    sense: OptimizationSense = Field(..., description="Optimization sense")
    
    # Solver options
    solver: Optional[str] = Field(default=None, description="Preferred solver")
    verbose: bool = Field(default=False, description="Verbose output")
    max_iters: Optional[int] = Field(default=None, description="Maximum iterations")

    def get_variables(self) -> List[BaseVariable]:
        """Get all variables in the problem."""
        return self.variables

    def get_constraints(self) -> List[BaseConstraint]:
        """Get all constraints in the problem."""
        return self.constraints

    def validate(self) -> bool:
        """Validate the problem definition."""
        if not self.variables:
            return False
        if not self.objective:
            return False
        
        # Check that all variable names are unique
        var_names = [var.name for var in self.variables]
        if len(var_names) != len(set(var_names)):
            return False
            
        return True


class CVXPYSolution(BaseSolution):
    """Model representing a solution to a CVXPY problem."""

    values: Dict[str, Any] = Field(..., description="Variable values")
    objective_value: Optional[float] = Field(default=None, description="Objective function value")
    status: str = Field(..., description="Solver status")
    dual_values: Optional[Dict[int, Any]] = Field(default=None, description="Dual values for constraints")
    
    # CVXPY-specific properties
    solve_time: Optional[float] = Field(default=None, description="Solve time in seconds")
    num_iterations: Optional[int] = Field(default=None, description="Number of iterations")
    solver_stats: Optional[Dict[str, Any]] = Field(default=None, description="Solver statistics")
    problem_value: Optional[float] = Field(default=None, description="Problem value")

    def get_variable_values(self) -> Dict[str, Any]:
        """Get values for all variables."""
        return self.values

    def get_dual_values(self) -> Optional[Dict[str, Any]]:
        """Get dual values for constraints."""
        if self.dual_values is None:
            return None
        return {f"constraint_{i}": value for i, value in self.dual_values.items()}

    @property
    def is_optimal(self) -> bool:
        """Whether solution is optimal."""
        return self.status.lower() in ["optimal", "optimal_inaccurate"]

    @property
    def is_feasible(self) -> bool:
        """Whether solution is feasible."""
        return self.status.lower() in ["optimal", "optimal_inaccurate", "unbounded", "unbounded_inaccurate"]
