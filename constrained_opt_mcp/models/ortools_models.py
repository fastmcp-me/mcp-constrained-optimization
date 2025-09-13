"""
OR-Tools constraint programming and combinatorial optimization models.
"""

from enum import Enum
from typing import Any, Optional, List, Dict, Tuple

from pydantic import BaseModel, Field

from ..core.base_models import BaseVariable, BaseConstraint, BaseProblem, BaseSolution
from ..core.problem_types import ProblemType, OptimizationSense, VariableType, ConstraintType


class ORToolsVariableType(str, Enum):
    """Enum for supported variable types in OR-Tools."""

    BOOLEAN = "boolean"
    INTEGER = "integer"
    INTERVAL = "interval"


class ORToolsObjectiveType(str, Enum):
    """Enum for optimization objective types."""

    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
    FEASIBILITY = "feasibility"  # Just find a feasible solution


class ORToolsVariable(BaseVariable):
    """Model representing a variable in an OR-Tools problem."""

    name: str = Field(..., description="Variable name")
    var_type: VariableType = Field(..., description="Variable type")
    description: str = Field(default="", description="Variable description")
    
    # OR-Tools specific properties
    type: ORToolsVariableType = Field(..., description="OR-Tools variable type")
    domain: Optional[Tuple[int, int]] = Field(default=None, description="Domain for integer variables")
    shape: Optional[List[int]] = Field(default=None, description="Shape for array variables")
    values: Optional[List[Any]] = Field(default=None, description="Possible values for categorical variables")

    def get_bounds(self) -> Tuple[Optional[float], Optional[float]]:
        """Get variable bounds (lower, upper)."""
        if self.domain:
            return float(self.domain[0]), float(self.domain[1])
        return None, None

    def get_var_type(self) -> VariableType:
        """Convert to base variable type."""
        mapping = {
            ORToolsVariableType.BOOLEAN: VariableType.BOOLEAN,
            ORToolsVariableType.INTEGER: VariableType.INTEGER,
            ORToolsVariableType.INTERVAL: VariableType.REAL,
        }
        return mapping[self.type]


class ORToolsConstraint(BaseConstraint):
    """Model representing a constraint in an OR-Tools problem."""

    expression: str = Field(..., description="Constraint expression")
    description: str = Field(default="", description="Constraint description")
    
    # OR-Tools specific properties
    constraint_type: ConstraintType = Field(default=ConstraintType.LOGICAL, description="Type of constraint")
    weight: Optional[float] = Field(default=None, description="Soft constraint weight")
    is_soft: bool = Field(default=False, description="Whether constraint is soft")

    def is_linear(self) -> bool:
        """Check if constraint is linear."""
        # OR-Tools constraints are typically linear for CP
        # but can be non-linear for certain constraint types
        non_linear_indicators = ["**", "^", "sqrt", "log", "exp", "sin", "cos"]
        expr_lower = self.expression.lower()
        return not any(indicator in expr_lower for indicator in non_linear_indicators)


class ORToolsObjective(BaseModel):
    """Model representing an optimization objective."""

    type: ORToolsObjectiveType = Field(default=ORToolsObjectiveType.FEASIBILITY, description="Objective type")
    expression: Optional[str] = Field(default=None, description="Objective expression")
    description: str = Field(default="", description="Objective description")
    
    # OR-Tools specific properties
    variable: Optional[str] = Field(default=None, description="Variable to optimize")
    weight: Optional[float] = Field(default=1.0, description="Objective weight")


class ORToolsProblem(BaseProblem):
    """Model representing a complete OR-Tools constraint programming problem."""

    variables: List[ORToolsVariable] = Field(..., description="Problem variables")
    constraints: List[ORToolsConstraint] = Field(..., description="Problem constraints")
    objective: Optional[ORToolsObjective] = Field(default=None, description="Problem objective")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Problem parameters")
    description: str = Field(default="", description="Problem description")
    
    # Base problem properties
    problem_type: ProblemType = Field(default=ProblemType.CONSTRAINT_PROGRAMMING, description="Problem type")
    sense: OptimizationSense = Field(..., description="Optimization sense")
    
    # OR-Tools specific properties
    solver_type: str = Field(default="cp", description="Solver type (cp, sat, etc.)")
    time_limit: Optional[float] = Field(default=None, description="Time limit in seconds")
    search_strategy: Optional[str] = Field(default=None, description="Search strategy")
    log_search_progress: bool = Field(default=False, description="Log search progress")

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
        
        # Check that all variable names are unique
        var_names = [var.name for var in self.variables]
        if len(var_names) != len(set(var_names)):
            return False
            
        return True


class ORToolsSolution(BaseSolution):
    """Model representing a solution to an OR-Tools problem."""

    values: Dict[str, Any] = Field(..., description="Variable values")
    is_feasible: bool = Field(..., description="Whether solution is feasible")
    status: str = Field(..., description="Solver status")
    objective_value: Optional[float] = Field(default=None, description="Objective function value")
    
    # OR-Tools specific properties
    solve_time: Optional[float] = Field(default=None, description="Solve time in seconds")
    statistics: Optional[Dict[str, Any]] = Field(default=None, description="Solver statistics")
    num_solutions: Optional[int] = Field(default=None, description="Number of solutions found")
    search_progress: Optional[Dict[str, Any]] = Field(default=None, description="Search progress information")

    def get_variable_values(self) -> Dict[str, Any]:
        """Get values for all variables."""
        return self.values

    def get_dual_values(self) -> Optional[Dict[str, Any]]:
        """Get dual values for constraints (not typically available for CP)."""
        return None

    @property
    def is_optimal(self) -> bool:
        """Whether solution is optimal."""
        return self.status.lower() in ["optimal", "feasible"] and self.is_feasible
