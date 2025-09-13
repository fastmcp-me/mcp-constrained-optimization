"""
Base model classes for the constrained optimization MCP server.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from .problem_types import ProblemType, OptimizationSense, VariableType, ConstraintType


class BaseVariable(BaseModel, ABC):
    """Base class for optimization variables."""
    
    name: str = Field(..., description="Variable name")
    var_type: VariableType = Field(..., description="Variable type")
    description: str = Field(default="", description="Variable description")
    
    @abstractmethod
    def get_bounds(self) -> tuple[Optional[float], Optional[float]]:
        """Get variable bounds (lower, upper)."""
        pass


class BaseConstraint(BaseModel, ABC):
    """Base class for optimization constraints."""
    
    expression: str = Field(..., description="Constraint expression")
    constraint_type: ConstraintType = Field(..., description="Type of constraint")
    description: str = Field(default="", description="Constraint description")
    
    @abstractmethod
    def is_linear(self) -> bool:
        """Check if constraint is linear."""
        pass


class BaseProblem(BaseModel, ABC):
    """Base class for optimization problems."""
    
    problem_type: ProblemType = Field(..., description="Type of optimization problem")
    sense: OptimizationSense = Field(..., description="Optimization sense")
    description: str = Field(default="", description="Problem description")
    
    @abstractmethod
    def get_variables(self) -> List[BaseVariable]:
        """Get all variables in the problem."""
        pass
    
    @abstractmethod
    def get_constraints(self) -> List[BaseConstraint]:
        """Get all constraints in the problem."""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate the problem definition."""
        pass


class BaseSolution(BaseModel, ABC):
    """Base class for optimization solutions."""
    
    status: str = Field(..., description="Solution status")
    is_optimal: bool = Field(default=False, description="Whether solution is optimal")
    is_feasible: bool = Field(default=False, description="Whether solution is feasible")
    objective_value: Optional[float] = Field(default=None, description="Objective function value")
    
    @abstractmethod
    def get_variable_values(self) -> Dict[str, Any]:
        """Get values for all variables."""
        pass
    
    @abstractmethod
    def get_dual_values(self) -> Optional[Dict[str, Any]]:
        """Get dual values for constraints (if available)."""
        pass


class ProblemMetadata(BaseModel):
    """Metadata for optimization problems."""
    
    problem_id: str = Field(..., description="Unique problem identifier")
    created_at: str = Field(..., description="Creation timestamp")
    solver_used: Optional[str] = Field(default=None, description="Solver backend used")
    solve_time: Optional[float] = Field(default=None, description="Solve time in seconds")
    memory_used: Optional[float] = Field(default=None, description="Memory used in MB")
    iterations: Optional[int] = Field(default=None, description="Number of iterations")
    
    # Problem characteristics
    n_variables: int = Field(..., description="Number of variables")
    n_constraints: int = Field(..., description="Number of constraints")
    n_integer_vars: int = Field(default=0, description="Number of integer variables")
    n_binary_vars: int = Field(default=0, description="Number of binary variables")
    
    # Solver-specific metadata
    solver_metadata: Dict[str, Any] = Field(default_factory=dict, description="Solver-specific metadata")


class SolverOptions(BaseModel):
    """Options for optimization solvers."""
    
    time_limit: Optional[float] = Field(default=None, description="Time limit in seconds")
    memory_limit: Optional[float] = Field(default=None, description="Memory limit in MB")
    tolerance: Optional[float] = Field(default=1e-6, description="Numerical tolerance")
    max_iterations: Optional[int] = Field(default=None, description="Maximum iterations")
    output_flag: bool = Field(default=True, description="Enable solver output")
    
    # Solver-specific options
    solver_options: Dict[str, Any] = Field(default_factory=dict, description="Solver-specific options")
