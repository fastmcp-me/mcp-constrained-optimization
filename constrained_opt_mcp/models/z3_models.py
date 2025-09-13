"""
Z3 SMT solver models for constraint satisfaction and logical optimization problems.
"""

from enum import Enum
from typing import Union, Optional, List, Dict, Any

import z3
from pydantic import BaseModel, Field

from ..core.base_models import BaseVariable, BaseConstraint, BaseProblem, BaseSolution
from ..core.problem_types import ProblemType, OptimizationSense, VariableType, ConstraintType

Z3Value = bool | int | float | str
Z3Ref = z3.BoolRef | z3.ArithRef | z3.ExprRef
Z3Sort = Union[z3.BoolSort, z3.IntSort, z3.RealSort, z3.StringSort]  # noqa: UP007


class Z3VariableType(str, Enum):
    """Variable types in Z3."""

    INTEGER = "integer"
    REAL = "real"
    BOOLEAN = "boolean"
    STRING = "string"


class Z3Variable(BaseVariable):
    """Typed variable in a Z3 problem."""

    name: str = Field(..., description="Variable name")
    type: Z3VariableType = Field(..., description="Z3 variable type")
    description: str = Field(default="", description="Variable description")
    
    # Z3-specific properties
    lower_bound: Optional[float] = Field(default=None, description="Lower bound")
    upper_bound: Optional[float] = Field(default=None, description="Upper bound")
    domain: Optional[List[Any]] = Field(default=None, description="Discrete domain values")

    def get_bounds(self) -> tuple[Optional[float], Optional[float]]:
        """Get variable bounds (lower, upper)."""
        return self.lower_bound, self.upper_bound

    def get_var_type(self) -> VariableType:
        """Convert to base variable type."""
        mapping = {
            Z3VariableType.INTEGER: VariableType.INTEGER,
            Z3VariableType.REAL: VariableType.REAL,
            Z3VariableType.BOOLEAN: VariableType.BOOLEAN,
            Z3VariableType.STRING: VariableType.STRING,
        }
        return mapping[self.type]


class Z3Constraint(BaseConstraint):
    """Constraint in a Z3 problem."""

    expression: str = Field(..., description="Constraint expression as string")
    description: str = Field(default="", description="Constraint description")
    
    # Z3-specific properties
    constraint_type: ConstraintType = Field(default=ConstraintType.LOGICAL, description="Type of constraint")
    weight: Optional[float] = Field(default=None, description="Soft constraint weight")

    def is_linear(self) -> bool:
        """Check if constraint is linear."""
        # Simple heuristic - could be enhanced with actual parsing
        linear_indicators = ["+", "-", "*", "==", "!=", "<=", ">=", "<", ">"]
        non_linear_indicators = ["**", "^", "sqrt", "log", "exp", "sin", "cos"]
        
        expr_lower = self.expression.lower()
        has_non_linear = any(indicator in expr_lower for indicator in non_linear_indicators)
        return not has_non_linear and any(indicator in expr_lower for indicator in linear_indicators)


class Z3Problem(BaseProblem):
    """Complete Z3 constraint satisfaction problem."""
    
    model_config = {"arbitrary_types_allowed": True}

    variables: List[Z3Variable] = Field(..., description="Problem variables")
    constraints: List[Z3Constraint] = Field(..., description="Problem constraints")
    description: str = Field(default="", description="Problem description")
    
    # Z3-specific properties
    problem_type: ProblemType = Field(default=ProblemType.CONSTRAINT_SATISFACTION, description="Problem type")
    sense: OptimizationSense = Field(default=OptimizationSense.SATISFY, description="Optimization sense")
    objective: Optional[str] = Field(default=None, description="Objective function expression")
    
    # Solver options
    timeout: Optional[int] = Field(default=None, description="Timeout in milliseconds")
    random_seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")

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
        if not self.constraints:
            return False
        
        # Check that all variable names are unique
        var_names = [var.name for var in self.variables]
        if len(var_names) != len(set(var_names)):
            return False
            
        return True


class Z3Solution(BaseSolution):
    """Solution to a Z3 problem."""
    
    model_config = {"arbitrary_types_allowed": True}

    values: Dict[str, Z3Value] = Field(..., description="Variable values")
    is_satisfiable: bool = Field(..., description="Whether problem is satisfiable")
    status: str = Field(..., description="Solver status")
    
    # Z3-specific properties
    model: Optional[z3.ModelRef] = Field(default=None, description="Z3 model object")
    statistics: Optional[Dict[str, Any]] = Field(default=None, description="Solver statistics")
    solve_time: Optional[float] = Field(default=None, description="Solve time in seconds")

    def get_variable_values(self) -> Dict[str, Any]:
        """Get values for all variables."""
        return self.values

    def get_dual_values(self) -> Optional[Dict[str, Any]]:
        """Get dual values for constraints (not applicable for Z3)."""
        return None

    @property
    def is_optimal(self) -> bool:
        """Whether solution is optimal (always True for Z3 if satisfiable)."""
        return self.is_satisfiable

    @property
    def is_feasible(self) -> bool:
        """Whether solution is feasible."""
        return self.is_satisfiable
