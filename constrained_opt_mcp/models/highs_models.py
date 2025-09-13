"""
HiGHS linear and mixed-integer programming models.
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Tuple

from pydantic import BaseModel, Field

from ..core.base_models import BaseVariable, BaseConstraint, BaseProblem, BaseSolution
from ..core.problem_types import ProblemType, OptimizationSense, VariableType, ConstraintType


class HiGHSSense(str, Enum):
    """Optimization sense for HiGHs problems."""

    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


class HiGHSVariableType(str, Enum):
    """Variable types in HiGHs."""

    CONTINUOUS = "cont"
    INTEGER = "int"
    BINARY = "bin"


class HiGHSConstraintSense(str, Enum):
    """Constraint directions in HiGHs."""

    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    EQUAL = "="


class HiGHSPresolve(str, Enum):
    """Presolve options for HiGHs."""

    OFF = "off"
    CHOOSE = "choose"
    ON = "on"


class HiGHSSolver(str, Enum):
    """Solver options for HiGHs."""

    SIMPLEX = "simplex"
    CHOOSE = "choose"
    IPM = "ipm"
    PDLP = "pdlp"


class HiGHSParallel(str, Enum):
    """Parallel options for HiGHs."""

    OFF = "off"
    CHOOSE = "choose"
    ON = "on"


class HiGHSStatus(str, Enum):
    """Solver status values for HiGHs."""

    OPTIMAL = "optimal"
    INFEASIBLE = "infeasible"
    UNBOUNDED = "unbounded"
    TIME_LIMIT = "time_limit"
    ITERATION_LIMIT = "iteration_limit"
    ERROR = "error"
    UNKNOWN = "unknown"


class HiGHSVariable(BaseVariable):
    """Variable specification for HiGHs."""

    name: str = Field(..., description="Variable name")
    var_type: VariableType = Field(..., description="Variable type")
    description: str = Field(default="", description="Variable description")
    
    # HiGHS-specific properties
    lb: Optional[float] = Field(default=None, description="Lower bound")
    ub: Optional[float] = Field(default=None, description="Upper bound")
    type: HiGHSVariableType = Field(default=HiGHSVariableType.CONTINUOUS, description="HiGHS variable type")

    def get_bounds(self) -> Tuple[Optional[float], Optional[float]]:
        """Get variable bounds (lower, upper)."""
        return self.lb, self.ub

    def get_var_type(self) -> VariableType:
        """Convert to base variable type."""
        mapping = {
            HiGHSVariableType.CONTINUOUS: VariableType.REAL,
            HiGHSVariableType.INTEGER: VariableType.INTEGER,
            HiGHSVariableType.BINARY: VariableType.BINARY,
        }
        return mapping[self.type]


class HiGHSSparseMatrix(BaseModel):
    """Sparse matrix representation for constraints."""

    rows: List[int] = Field(..., description="Row indices of non-zero coefficients (0-indexed)")
    cols: List[int] = Field(..., description="Column indices of non-zero coefficients (0-indexed)")
    values: List[float] = Field(..., description="Non-zero coefficient values")
    shape: Tuple[int, int] = Field(..., description="[num_constraints, num_variables]")


class HiGHSConstraint(BaseConstraint):
    """Constraint specification for HiGHs."""

    expression: str = Field(..., description="Constraint expression")
    description: str = Field(default="", description="Constraint description")
    
    # HiGHS-specific properties
    constraint_type: ConstraintType = Field(default=ConstraintType.LINEAR_INEQUALITY, description="Type of constraint")
    sense: HiGHSConstraintSense = Field(..., description="Constraint direction")
    rhs: float = Field(..., description="Right-hand side value")

    def is_linear(self) -> bool:
        """Check if constraint is linear."""
        # HiGHS constraints are always linear
        return True


class HiGHSConstraints(BaseModel):
    """Constraint specification for HiGHs."""

    # Dense format (for small problems)
    dense: Optional[List[List[float]]] = Field(
        default=None, description="2D array where each row is a constraint"
    )

    # OR Sparse format (for large problems with many zeros)
    sparse: Optional[HiGHSSparseMatrix] = Field(
        default=None, description="Sparse matrix representation"
    )

    sense: List[HiGHSConstraintSense] = Field(..., description="Constraint directions")
    rhs: List[float] = Field(..., description="Right-hand side values")


class HiGHSObjective(BaseModel):
    """Objective function specification for HiGHs."""

    linear: List[float] = Field(..., description="Coefficients for each variable")
    quadratic: Optional[List[List[float]]] = Field(default=None, description="Quadratic coefficients matrix")


class HiGHSOptions(BaseModel):
    """Options for HiGHs solver."""

    # Solver Control
    time_limit: Optional[float] = Field(default=None, description="Time limit in seconds")
    presolve: Optional[HiGHSPresolve] = Field(default=None, description="Presolve option")
    solver: Optional[HiGHSSolver] = Field(default=None, description="Solver algorithm")
    parallel: Optional[HiGHSParallel] = Field(default=None, description="Parallel option")
    threads: Optional[int] = Field(default=None, description="Number of threads (0=automatic)")
    random_seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")

    # Tolerances
    primal_feasibility_tolerance: Optional[float] = Field(default=None, description="Default: 1e-7")
    dual_feasibility_tolerance: Optional[float] = Field(default=None, description="Default: 1e-7")
    ipm_optimality_tolerance: Optional[float] = Field(default=None, description="Default: 1e-8")
    infinite_cost: Optional[float] = Field(default=None, description="Default: 1e20")
    infinite_bound: Optional[float] = Field(default=None, description="Default: 1e20")

    # Simplex Options
    simplex_strategy: Optional[int] = Field(default=None, description="0-4: algorithm strategy")
    simplex_scale_strategy: Optional[int] = Field(default=None, description="0-5: scaling strategy")
    simplex_dual_edge_weight_strategy: Optional[int] = Field(default=None, description="-1 to 2: pricing")
    simplex_iteration_limit: Optional[int] = Field(default=None, description="Max iterations")

    # MIP Options
    mip_detect_symmetry: Optional[bool] = Field(default=None, description="Detect symmetry")
    mip_max_nodes: Optional[int] = Field(default=None, description="Max branch-and-bound nodes")
    mip_rel_gap: Optional[float] = Field(default=None, description="Relative gap tolerance")
    mip_abs_gap: Optional[float] = Field(default=None, description="Absolute gap tolerance")
    mip_feasibility_tolerance: Optional[float] = Field(default=None, description="MIP feasibility tolerance")

    # Logging
    output_flag: Optional[bool] = Field(default=None, description="Enable solver output")
    log_to_console: Optional[bool] = Field(default=None, description="Console logging")
    highs_debug_level: Optional[int] = Field(default=None, description="0-4: debug verbosity")

    # Algorithm-specific
    ipm_iteration_limit: Optional[int] = Field(default=None, description="IPM max iterations")
    pdlp_scaling: Optional[bool] = Field(default=None, description="PDLP scaling")
    pdlp_iteration_limit: Optional[int] = Field(default=None, description="PDLP max iterations")

    # File I/O
    write_solution_to_file: Optional[bool] = Field(default=None, description="Write solution to file")
    solution_file: Optional[str] = Field(default=None, description="Solution file path")
    write_solution_style: Optional[int] = Field(default=None, description="Solution format style")


class HiGHSProblemSpec(BaseModel):
    """Problem specification for HiGHs."""

    sense: HiGHSSense = Field(..., description="Optimization sense")
    objective: HiGHSObjective = Field(..., description="Objective function")
    variables: List[HiGHSVariable] = Field(..., description="Variable specifications")
    constraints: HiGHSConstraints = Field(..., description="Constraint specifications")


class HiGHSProblem(BaseProblem):
    """Complete HiGHS optimization problem."""

    problem: HiGHSProblemSpec = Field(..., description="Problem specification")
    options: Optional[HiGHSOptions] = Field(default=None, description="Solver options")
    
    # Base problem properties
    problem_type: ProblemType = Field(default=ProblemType.LINEAR_PROGRAMMING, description="Problem type")
    sense: OptimizationSense = Field(..., description="Optimization sense")
    description: str = Field(default="", description="Problem description")

    def get_variables(self) -> List[BaseVariable]:
        """Get all variables in the problem."""
        return self.problem.variables

    def get_constraints(self) -> List[BaseConstraint]:
        """Get all constraints in the problem."""
        # Convert HiGHS constraints to base constraints
        constraints = []
        for i, sense in enumerate(self.problem.constraints.sense):
            constraint = HiGHSConstraint(
                expression=f"constraint_{i}",
                sense=sense,
                rhs=self.problem.constraints.rhs[i],
                description=f"Constraint {i}"
            )
            constraints.append(constraint)
        return constraints

    def validate(self) -> bool:
        """Validate the problem definition."""
        if not self.problem.variables:
            return False
        if not self.problem.constraints.sense:
            return False
        
        # Check that all variable names are unique
        var_names = [var.name for var in self.problem.variables]
        if len(var_names) != len(set(var_names)):
            return False
            
        return True


class HiGHSSolution(BaseSolution):
    """Solution to a HiGHs problem."""

    values: Dict[str, float] = Field(..., description="Variable values")
    objective_value: Optional[float] = Field(default=None, description="Optimal objective value")
    status: HiGHSStatus = Field(..., description="Solver status")
    
    # HiGHS-specific properties
    is_optimal: bool = Field(default=False, description="Whether solution is optimal")
    solve_time: Optional[float] = Field(default=None, description="Solve time in seconds")
    iterations: Optional[int] = Field(default=None, description="Number of iterations")
    dual_values: Optional[List[float]] = Field(default=None, description="Dual values for constraints")
    reduced_costs: Optional[List[float]] = Field(default=None, description="Reduced costs for variables")
    solver_stats: Optional[Dict[str, Any]] = Field(default=None, description="Solver statistics")

    def get_variable_values(self) -> Dict[str, Any]:
        """Get values for all variables."""
        return self.values

    def get_dual_values(self) -> Optional[Dict[str, Any]]:
        """Get dual values for constraints."""
        if self.dual_values is None:
            return None
        return {f"constraint_{i}": value for i, value in enumerate(self.dual_values)}

    @property
    def is_feasible(self) -> bool:
        """Whether solution is feasible."""
        return self.status in [HiGHSStatus.OPTIMAL, HiGHSStatus.UNBOUNDED]
