"""
CVXPY convex optimization solver implementation.
"""

from typing import Any, Dict, Union, Optional
import time

import cvxpy as cp
import numpy as np
from returns.result import Failure, Result, Success

from ..models.cvxpy_models import (
    CVXPYProblem,
    CVXPYSolution,
    CVXPYVariable,
    CVXPYConstraint,
    CVXPYObjective,
    ObjectiveType,
)

# Type alias for CVXPY expressions
CVXPYExpr = Union[cp.Expression, cp.Constraint, np.ndarray]  # noqa: UP007


def create_variable(var: CVXPYVariable) -> cp.Variable:
    """Create a CVXPY variable from a CVXPYVariable model.

    Args:
        var: CVXPYVariable model

    Returns:
        CVXPY variable
    """
    kwargs = {}
    
    # Add constraints based on variable properties
    if var.nonneg:
        kwargs["nonneg"] = True
    if var.nonpos:
        kwargs["nonpos"] = True
    if var.symmetric:
        kwargs["symmetric"] = True
    if var.diag:
        kwargs["diag"] = True
    if var.hermitian:
        kwargs["hermitian"] = True
    if var.complex:
        kwargs["complex"] = True
    
    return cp.Variable(var.shape, name=var.name, **kwargs)


def parse_expression(
    expr_str: str, variables: Dict[str, cp.Variable], params: Dict[str, Any]
) -> CVXPYExpr:
    """Parse a CVXPY expression string.

    Args:
        expr_str: String representation of the expression
        variables: Dictionary of variable names to CVXPY variables
        params: Dictionary of parameter names to values

    Returns:
        Parsed CVXPY expression
    """
    # Create a local dictionary with variables and parameters
    local_dict = {
        **variables,
        **params,
        "cp": cp,
        "np": np,
    }

    # Evaluate the expression in the context of the local dictionary
    return eval(expr_str, {"__builtins__": {}}, local_dict)


def solve_cvxpy_problem(problem: CVXPYProblem) -> Result[CVXPYSolution, str]:
    """Solve a CVXPY optimization problem.

    Args:
        problem: The problem definition

    Returns:
        Result containing a CVXPYSolution or an error message
    """
    try:
        # Validate problem
        if not problem.validate():
            return Failure("Invalid problem definition")

        start_time = time.time()
        
        # Create variables
        variables: Dict[str, cp.Variable] = {}
        for var in problem.variables:
            variables[var.name] = create_variable(var)

        # Parse objective
        objective_expr = parse_expression(
            problem.objective.expression, variables, problem.parameters
        )
        objective = (
            cp.Minimize(objective_expr)
            if problem.objective.type == ObjectiveType.MINIMIZE
            else cp.Maximize(objective_expr)
        )

        # Parse constraints
        constraints = []
        for constraint in problem.constraints:
            constraint_expr = parse_expression(
                constraint.expression, variables, problem.parameters
            )
            constraints.append(constraint_expr)

        # Create and solve the problem
        prob = cp.Problem(objective, constraints)
        
        # Set solver options if specified
        solver_kwargs = {}
        if problem.solver:
            solver_kwargs["solver"] = problem.solver
        if problem.max_iters:
            solver_kwargs["max_iters"] = problem.max_iters
            
        result = prob.solve(verbose=problem.verbose, **solver_kwargs)
        solve_time = time.time() - start_time

        # Extract solution
        values = {name: var.value for name, var in variables.items()}
        dual_values = {
            i: constraint.dual_value
            for i, constraint in enumerate(constraints)
            if hasattr(constraint, "dual_value") and constraint.dual_value is not None
        }

        # Get solver statistics
        solver_stats = {}
        if hasattr(prob, "solver_stats"):
            solver_stats = prob.solver_stats

        return Success(
            CVXPYSolution(
                values=values,
                objective_value=float(result) if result is not None else None,
                status=prob.status,
                dual_values=dual_values if dual_values else None,
                solve_time=solve_time,
                solver_stats=solver_stats,
                problem_value=prob.value,
            )
        )
    except Exception as e:
        return Failure(f"Error solving CVXPY problem: {e!s}")
