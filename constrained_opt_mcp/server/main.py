#!/usr/bin/env python3
"""
Constrained Optimization MCP Server

A general-purpose Model Context Protocol server for solving combinatorial 
optimization problems with logical and numerical constraints.

This server provides tools for:
- Constraint satisfaction problems (Z3)
- Convex optimization (CVXPY)
- Linear and mixed-integer programming (HiGHS)
- Constraint programming (OR-Tools)
- Financial optimization problems
"""

import json
import sys
from typing import Any, List

from fastmcp import FastMCP
from mcp.types import TextContent
from returns.result import Failure, Success

from ..models import (
    Z3Problem, Z3Solution, Z3Variable, Z3Constraint,
    CVXPYProblem, CVXPYSolution, CVXPYVariable, CVXPYConstraint,
    HiGHSProblem, HiGHSSolution, HiGHSVariable, HiGHSConstraint,
    ORToolsProblem, ORToolsSolution, ORToolsVariable, ORToolsConstraint
)
from ..solvers import (
    solve_z3_problem,
    solve_cvxpy_problem,
    solve_highs_problem,
    solve_ortools_problem
)
from ..core.problem_types import ProblemType, OptimizationSense, VariableType, ConstraintType

app = FastMCP(
    name="constrained-opt-mcp",
    version="1.0.0",
    description="A general-purpose MCP server for solving combinatorial optimization problems with logical and numerical constraints",
    dependencies=[
        "z3-solver>=4.14.1.0",
        "pydantic>=2.0.0",
        "returns>=0.20.0",
        "fastmcp>=0.1.0",
        "cvxpy>=1.6.0",
        "ortools<9.15.0",
        "highspy>=1.11.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "jupyter>=1.0.0",
        "ipywidgets>=8.0.0",
    ],
)


@app.tool("solve_constraint_satisfaction")
async def solve_constraint_satisfaction(
    variables: List[dict[str, str]],
    constraints: List[str],
    description: str = "",
    timeout: int = None,
) -> List[TextContent]:
    """
    Solve constraint satisfaction problems using Z3 SMT solver.
    
    This tool is ideal for logical reasoning, puzzle solving, and constraint satisfaction
    problems where you need to find values that satisfy a set of logical constraints.
    
    Args:
        variables: List of variable definitions with 'name' and 'type' fields
        constraints: List of constraint expressions as strings
        description: Optional problem description
        timeout: Optional timeout in milliseconds
        
    Returns:
        Solution results including variable values and satisfiability status
        
    Example:
        variables = [
            {"name": "x", "type": "integer"},
            {"name": "y", "type": "integer"}
        ]
        constraints = [
            "x + y == 10",
            "x - y == 2"
        ]
    """
    try:
        # Convert to Z3 problem
        problem_variables = []
        for var in variables:
            if "name" not in var or "type" not in var:
                return [
                    TextContent(
                        type="text",
                        text="Each variable must have 'name' and 'type' fields",
                    )
                ]

            try:
                from ..models.z3_models import Z3VariableType
                var_type = Z3VariableType(var["type"])
            except ValueError:
                return [
                    TextContent(
                        type="text",
                        text=(
                            f"Invalid variable type: {var['type']}. "
                            f"Must be one of: integer, real, boolean, string"
                        ),
                    )
                ]

            problem_variables.append(Z3Variable(
                name=var["name"], 
                type=var_type,
                description=var.get("description", "")
            ))

        problem_constraints = [Z3Constraint(expression=expr) for expr in constraints]

        problem = Z3Problem(
            variables=problem_variables,
            constraints=problem_constraints,
            description=description,
            timeout=timeout,
        )

        # Solve the problem
        result = solve_z3_problem(problem)

        match result:
            case Success(solution):
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "values": solution.values,
                                "is_satisfiable": solution.is_satisfiable,
                                "status": solution.status,
                                "solve_time": solution.solve_time,
                            }
                        ),
                    )
                ]
            case Failure(error):
                return [TextContent(type="text", text=f"Error solving problem: {error}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error in solve_constraint_satisfaction: {e!s}")]


@app.tool("solve_convex_optimization")
async def solve_convex_optimization(
    variables: List[dict[str, Any]],
    objective_type: str,
    objective_expr: str,
    constraints: List[str],
    parameters: dict[str, Any] = None,
    description: str = "",
) -> List[TextContent]:
    """
    Solve convex optimization problems using CVXPY.
    
    This tool is ideal for mathematical optimization problems with convex objectives
    and constraints, including linear programming, quadratic programming, and
    semidefinite programming.
    
    Args:
        variables: List of variable definitions with 'name' and 'shape'
        objective_type: Either 'minimize' or 'maximize'
        objective_expr: The objective function expression as a string
        constraints: List of constraint expressions as strings
        parameters: Dictionary of parameter values (e.g., matrices A, b)
        description: Optional problem description
        
    Returns:
        Solution results including variable values and objective value
        
    Example:
        variables = [{"name": "x", "shape": 2}]
        objective_type = "minimize"
        objective_expr = "cp.sum_squares(x)"
        constraints = ["x >= 0", "cp.sum(x) == 1"]
    """
    try:
        # Convert to CVXPY problem
        problem_variables = []
        for var in variables:
            if "name" not in var or "shape" not in var:
                return [
                    TextContent(
                        type="text",
                        text="Each variable must have 'name' and 'shape' fields",
                    )
                ]

            problem_variables.append(CVXPYVariable(**var))

        try:
            from ..models.cvxpy_models import ObjectiveType
            obj_type = ObjectiveType(objective_type)
        except ValueError:
            return [
                TextContent(
                    type="text",
                    text=(
                        f"Invalid objective type: {objective_type}. "
                        f"Must be one of: minimize, maximize"
                    ),
                )
            ]

        from ..models.cvxpy_models import CVXPYObjective, CVXPYConstraint
        objective = CVXPYObjective(type=obj_type, expression=objective_expr)
        problem_constraints = [CVXPYConstraint(expression=expr) for expr in constraints]

        problem = CVXPYProblem(
            variables=problem_variables,
            objective=objective,
            constraints=problem_constraints,
            parameters=parameters or {},
            description=description,
        )

        # Solve the problem
        result = solve_cvxpy_problem(problem)

        match result:
            case Success(solution):
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "values": {
                                    k: v.tolist() if hasattr(v, "tolist") else v
                                    for k, v in solution.values.items()
                                },
                                "objective_value": solution.objective_value,
                                "status": solution.status,
                                "solve_time": solution.solve_time,
                                "dual_values": {
                                    k: v.tolist() if hasattr(v, "tolist") else v
                                    for k, v in (solution.dual_values or {}).items()
                                },
                            }
                        ),
                    )
                ]
            case Failure(error):
                return [TextContent(type="text", text=f"Error solving problem: {error}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error in solve_convex_optimization: {e!s}")]


@app.tool("solve_linear_programming")
async def solve_linear_programming(
    sense: str,
    objective_coeffs: List[float],
    variables: List[dict[str, Any]],
    constraint_matrix: List[List[float]],
    constraint_senses: List[str],
    rhs_values: List[float],
    options: dict[str, Any] = None,
    description: str = "",
) -> List[TextContent]:
    """
    Solve linear and mixed-integer programming problems using HiGHS.
    
    This tool is ideal for linear programming, mixed-integer linear programming,
    and large-scale optimization problems with linear constraints.
    
    Args:
        sense: Optimization sense, either "minimize" or "maximize"
        objective_coeffs: List of objective function coefficients
        variables: List of variable definitions with optional bounds and types
        constraint_matrix: 2D list representing the constraint matrix (dense format)
        constraint_senses: List of constraint directions ("<=", ">=", "=")
        rhs_values: List of right-hand side values for constraints
        options: Optional solver options dictionary
        description: Optional problem description
        
    Returns:
        Solution results including variable values and objective value
        
    Example:
        sense = "minimize"
        objective_coeffs = [1.0, 2.0, 3.0]
        variables = [
            {"name": "x1", "lb": 0, "ub": 10, "type": "cont"},
            {"name": "x2", "lb": 0, "ub": None, "type": "int"},
            {"name": "x3", "lb": 0, "ub": 1, "type": "bin"}
        ]
        constraint_matrix = [[1, 1, 0], [0, 1, 1]]
        constraint_senses = ["<=", ">="]
        rhs_values = [5, 3]
    """
    try:
        # Validate sense
        try:
            from ..models.highs_models import HiGHSSense
            problem_sense = HiGHSSense(sense)
        except ValueError:
            return [
                TextContent(
                    type="text",
                    text=(
                        f"Invalid sense: {sense}. "
                        f"Must be one of: minimize, maximize"
                    ),
                )
            ]

        # Create objective
        from ..models.highs_models import HiGHSObjective
        objective = HiGHSObjective(linear=objective_coeffs)

        # Create variables
        problem_variables = []
        for i, var in enumerate(variables):
            var_name = var.get("name", f"x{i+1}")
            var_lb = var.get("lb", 0.0)
            var_ub = var.get("ub", None)
            var_type_str = var.get("type", "cont")

            try:
                from ..models.highs_models import HiGHSVariableType
                var_type = HiGHSVariableType(var_type_str)
            except ValueError:
                return [
                    TextContent(
                        type="text",
                        text=(
                            f"Invalid variable type: {var_type_str}. "
                            f"Must be one of: cont, int, bin"
                        ),
                    )
                ]

            from ..models.highs_models import HiGHSVariable
            problem_variables.append(
                HiGHSVariable(name=var_name, lb=var_lb, ub=var_ub, type=var_type)
            )

        # Create constraints
        constraint_sense_enums = []
        for sense_str in constraint_senses:
            try:
                from ..models.highs_models import HiGHSConstraintSense
                constraint_sense_enums.append(HiGHSConstraintSense(sense_str))
            except ValueError:
                return [
                    TextContent(
                        type="text",
                        text=(
                            f"Invalid constraint sense: {sense_str}. "
                            f"Must be one of: <=, >=, ="
                        ),
                    )
                ]

        from ..models.highs_models import HiGHSConstraints, HiGHSProblemSpec, HiGHSProblem, HiGHSOptions
        constraints = HiGHSConstraints(
            dense=constraint_matrix,
            sparse=None,
            sense=constraint_sense_enums,
            rhs=rhs_values,
        )

        # Create problem specification
        problem_spec = HiGHSProblemSpec(
            sense=problem_sense,
            objective=objective,
            variables=problem_variables,
            constraints=constraints,
        )

        # Create options if provided
        highs_options = None
        if options:
            highs_options = HiGHSOptions(**options)

        # Create full problem
        problem = HiGHSProblem(problem=problem_spec, options=highs_options)

        # Solve the problem
        result = solve_highs_problem(problem)

        match result:
            case Success(solution):
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "values": solution.values,
                                "objective_value": solution.objective_value,
                                "status": solution.status.value,
                                "solve_time": solution.solve_time,
                                "dual_values": solution.dual_values,
                                "reduced_costs": solution.reduced_costs,
                            }
                        ),
                    )
                ]
            case Failure(error):
                return [TextContent(type="text", text=f"Error solving problem: {error}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error in solve_linear_programming: {e!s}")]


@app.tool("solve_constraint_programming")
async def solve_constraint_programming(
    variables: List[dict[str, Any]],
    constraints: List[str],
    objective: dict[str, Any] = None,
    parameters: dict[str, Any] = None,
    description: str = "",
) -> List[TextContent]:
    """
    Solve constraint programming problems using OR-Tools.
    
    This tool is ideal for combinatorial optimization problems, scheduling,
    assignment problems, and constraint satisfaction with discrete variables.
    
    Args:
        variables: List of variable definitions with 'name', 'type', and optional 'domain'/'shape'
        constraints: List of constraint expressions as strings
        objective: Optional objective definition with 'type' and 'expression'
        parameters: Dictionary of solver parameters
        description: Optional problem description
        
    Returns:
        Solution results including variable values and feasibility status
        
    Example:
        variables = [
            {"name": "x", "type": "integer", "domain": [0, 10]},
            {"name": "y", "type": "boolean"}
        ]
        constraints = [
            "x + y >= 5",
            "x - y <= 3"
        ]
        objective = {"type": "minimize", "expression": "x + y"}
    """
    try:
        # Convert to OR-Tools problem
        problem_variables = []
        for var in variables:
            if "name" not in var or "type" not in var:
                return [
                    TextContent(
                        type="text",
                        text="Each variable must have 'name' and 'type' fields",
                    )
                ]

            try:
                from ..models.ortools_models import ORToolsVariableType
                var_type = ORToolsVariableType(var["type"])
            except ValueError:
                return [
                    TextContent(
                        type="text",
                        text=(
                            f"Invalid variable type: {var['type']}. "
                            f"Must be one of: boolean, integer, interval"
                        ),
                    )
                ]

            problem_variables.append(ORToolsVariable(**var))

        problem_constraints = [ORToolsConstraint(expression=expr) for expr in constraints]

        # Create objective if provided
        problem_objective = None
        if objective:
            try:
                from ..models.ortools_models import ORToolsObjectiveType
                obj_type = ORToolsObjectiveType(objective["type"])
                problem_objective = ORToolsObjective(
                    type=obj_type,
                    expression=objective.get("expression"),
                    description=objective.get("description", "")
                )
            except ValueError:
                return [
                    TextContent(
                        type="text",
                        text=(
                            f"Invalid objective type: {objective['type']}. "
                            f"Must be one of: minimize, maximize, feasibility"
                        ),
                    )
                ]

        problem = ORToolsProblem(
            variables=problem_variables,
            constraints=problem_constraints,
            objective=problem_objective,
            parameters=parameters or {},
            description=description,
        )

        # Solve the problem
        result = solve_ortools_problem(problem)

        match result:
            case Success(solution):
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "values": solution.values,
                                "is_feasible": solution.is_feasible,
                                "status": solution.status,
                                "objective_value": solution.objective_value,
                                "solve_time": solution.solve_time,
                                "statistics": solution.statistics,
                            }
                        ),
                    )
                ]
            case Failure(error):
                return [TextContent(type="text", text=f"Error solving problem: {error}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error in solve_constraint_programming: {e!s}")]


@app.tool("solve_portfolio_optimization")
async def solve_portfolio_optimization(
    assets: List[str],
    expected_returns: List[float],
    risk_factors: List[float],
    correlation_matrix: List[List[float]],
    max_allocations: List[float] = None,
    risk_budget: float = None,
    description: str = "",
) -> List[TextContent]:
    """
    Solve portfolio optimization problems using modern portfolio theory.
    
    This tool implements Markowitz mean-variance optimization to find optimal
    asset allocations that maximize expected return while constraining risk.
    
    Args:
        assets: List of asset names
        expected_returns: List of expected returns for each asset
        risk_factors: List of risk factors (standard deviations) for each asset
        correlation_matrix: Correlation matrix between assets
        max_allocations: Optional maximum allocation limits for each asset
        risk_budget: Optional maximum portfolio risk (variance)
        description: Optional problem description
        
    Returns:
        Optimal portfolio weights and performance metrics
        
    Example:
        assets = ["Bonds", "Stocks", "RealEstate", "Commodities"]
        expected_returns = [0.08, 0.12, 0.10, 0.15]
        risk_factors = [0.02, 0.15, 0.08, 0.20]
        correlation_matrix = [[1.0, 0.2, 0.3, 0.1], [0.2, 1.0, 0.6, 0.7], ...]
        max_allocations = [0.4, 0.6, 0.3, 0.2]
        risk_budget = 0.01
    """
    try:
        import numpy as np
        
        n_assets = len(assets)
        
        # Validate inputs
        if len(expected_returns) != n_assets:
            return [TextContent(type="text", text="Expected returns length must match number of assets")]
        if len(risk_factors) != n_assets:
            return [TextContent(type="text", text="Risk factors length must match number of assets")]
        if len(correlation_matrix) != n_assets or len(correlation_matrix[0]) != n_assets:
            return [TextContent(type="text", text="Correlation matrix must be square and match number of assets")]
        
        # Convert to numpy arrays
        expected_returns = np.array(expected_returns)
        risk_factors = np.array(risk_factors)
        correlation_matrix = np.array(correlation_matrix)
        
        # Create covariance matrix
        covariance_matrix = np.outer(risk_factors, risk_factors) * correlation_matrix
        
        # Set default max allocations if not provided
        if max_allocations is None:
            max_allocations = [1.0] * n_assets
        
        # Create CVXPY problem
        variables = [CVXPYVariable(name="weights", shape=n_assets)]
        
        # Create constraints
        constraint_exprs = [
            "cp.sum(weights) == 1",  # Budget constraint
            "weights >= 0",  # Non-negativity
        ]
        
        # Add individual allocation limits
        for i, max_alloc in enumerate(max_allocations):
            constraint_exprs.append(f"weights[{i}] <= {max_alloc}")
        
        # Add risk constraint if specified
        if risk_budget is not None:
            constraint_exprs.append("cp.quad_form(weights, covariance_matrix) <= risk_budget")
        
        constraints = [CVXPYConstraint(expression=expr) for expr in constraint_exprs]
        
        # Create objective (maximize expected return)
        from ..models.cvxpy_models import CVXPYObjective, ObjectiveType
        objective = CVXPYObjective(
            type=ObjectiveType.MAXIMIZE,
            expression="expected_returns.T @ weights"
        )
        
        problem = CVXPYProblem(
            variables=variables,
            objective=objective,
            constraints=constraints,
            parameters={
                "expected_returns": expected_returns,
                "covariance_matrix": covariance_matrix,
                "risk_budget": risk_budget,
            },
            description=description or "Portfolio optimization using modern portfolio theory",
        )
        
        # Solve the problem
        result = solve_cvxpy_problem(problem)
        
        match result:
            case Success(solution):
                if solution.status == "optimal":
                    weights = solution.values["weights"]
                    expected_return = solution.objective_value
                    
                    # Calculate portfolio risk
                    portfolio_risk = np.sqrt(weights.T @ covariance_matrix @ weights)
                    
                    # Calculate Sharpe ratio (assuming risk-free rate = 0)
                    sharpe_ratio = expected_return / portfolio_risk if portfolio_risk > 0 else 0
                    
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {
                                    "status": "optimal",
                                    "weights": {assets[i]: float(weights[i]) for i in range(n_assets)},
                                    "expected_return": float(expected_return),
                                    "portfolio_risk": float(portfolio_risk),
                                    "sharpe_ratio": float(sharpe_ratio),
                                    "solve_time": solution.solve_time,
                                }
                            ),
                        )
                    ]
                else:
                    return [TextContent(type="text", text=f"Optimization failed: {solution.status}")]
            case Failure(error):
                return [TextContent(type="text", text=f"Error solving portfolio optimization: {error}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error in solve_portfolio_optimization: {e!s}")]


def main() -> None:
    """Main function to run the MCP server."""
    print("Starting Constrained Optimization MCP server...", file=sys.stderr)
    app.run()


if __name__ == "__main__":
    main()
