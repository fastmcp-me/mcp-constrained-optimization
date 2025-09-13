"""
Tests for CVXPY convex optimization solver.
"""

import pytest
import numpy as np
from returns.result import Success, Failure

from constrained_opt_mcp.models.cvxpy_models import (
    CVXPYProblem, CVXPYVariable, CVXPYConstraint, CVXPYObjective,
    ObjectiveType
)
from constrained_opt_mcp.solvers.cvxpy_solver import solve_cvxpy_problem


class TestCVXPYSolver:
    """Test cases for CVXPY solver functionality."""

    def test_linear_programming(self):
        """Test solving linear programming problems."""
        variables = [CVXPYVariable(name="x", shape=2)]
        objective = CVXPYObjective(
            type=ObjectiveType.MINIMIZE,
            expression="cp.sum(x)"
        )
        constraints = [
            CVXPYConstraint(expression="x >= 0"),
            CVXPYConstraint(expression="cp.sum(x) == 1"),
        ]
        problem = CVXPYProblem(
            variables=variables,
            objective=objective,
            constraints=constraints,
            description="Linear programming test"
        )

        result = solve_cvxpy_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status == "optimal"
        assert solution.objective_value is not None
        assert len(solution.values["x"]) == 2

    def test_quadratic_programming(self):
        """Test solving quadratic programming problems."""
        variables = [CVXPYVariable(name="x", shape=2)]
        objective = CVXPYObjective(
            type=ObjectiveType.MINIMIZE,
            expression="cp.sum_squares(x)"
        )
        constraints = [
            CVXPYConstraint(expression="x >= 0"),
            CVXPYConstraint(expression="cp.sum(x) == 1"),
        ]
        problem = CVXPYProblem(
            variables=variables,
            objective=objective,
            constraints=constraints,
            description="Quadratic programming test"
        )

        result = solve_cvxpy_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status == "optimal"
        assert solution.objective_value is not None

    def test_least_squares_optimization(self):
        """Test solving least squares optimization."""
        # Create test data
        A = np.array([[1.0, -0.5], [0.5, 2.0], [0.0, 1.0]])
        b = np.array([2.0, 1.0, -1.0])
        
        variables = [CVXPYVariable(name="x", shape=2)]
        objective = CVXPYObjective(
            type=ObjectiveType.MINIMIZE,
            expression="cp.sum_squares(A @ x - b)"
        )
        constraints = [
            CVXPYConstraint(expression="x >= 0"),
            CVXPYConstraint(expression="x <= 1"),
        ]
        problem = CVXPYProblem(
            variables=variables,
            objective=objective,
            constraints=constraints,
            parameters={"A": A, "b": b},
            description="Least squares optimization test"
        )

        result = solve_cvxpy_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status == "optimal"
        assert solution.objective_value is not None

    def test_maximization_problem(self):
        """Test solving maximization problems."""
        variables = [CVXPYVariable(name="x", shape=2)]
        objective = CVXPYObjective(
            type=ObjectiveType.MAXIMIZE,
            expression="cp.sum(x)"
        )
        constraints = [
            CVXPYConstraint(expression="x >= 0"),
            CVXPYConstraint(expression="cp.sum(x) <= 1"),
        ]
        problem = CVXPYProblem(
            variables=variables,
            objective=objective,
            constraints=constraints,
            description="Maximization test"
        )

        result = solve_cvxpy_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status == "optimal"
        assert solution.objective_value is not None

    def test_matrix_variables(self):
        """Test solving problems with matrix variables."""
        variables = [CVXPYVariable(name="X", shape=(2, 2))]
        objective = CVXPYObjective(
            type=ObjectiveType.MINIMIZE,
            expression="cp.trace(X)"
        )
        constraints = [
            CVXPYConstraint(expression="X >= 0"),
            CVXPYConstraint(expression="cp.trace(X) >= 1"),
        ]
        problem = CVXPYProblem(
            variables=variables,
            objective=objective,
            constraints=constraints,
            description="Matrix variable test"
        )

        result = solve_cvxpy_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status == "optimal"
        assert solution.objective_value is not None

    def test_infeasible_problem(self):
        """Test handling of infeasible problems."""
        variables = [CVXPYVariable(name="x", shape=1)]
        objective = CVXPYObjective(
            type=ObjectiveType.MINIMIZE,
            expression="x[0]"
        )
        constraints = [
            CVXPYConstraint(expression="x >= 1"),
            CVXPYConstraint(expression="x <= 0"),
        ]
        problem = CVXPYProblem(
            variables=variables,
            objective=objective,
            constraints=constraints,
            description="Infeasible problem test"
        )

        result = solve_cvxpy_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status == "infeasible"

    def test_unbounded_problem(self):
        """Test handling of unbounded problems."""
        variables = [CVXPYVariable(name="x", shape=1)]
        objective = CVXPYObjective(
            type=ObjectiveType.MINIMIZE,
            expression="x[0]"
        )
        constraints = [
            CVXPYConstraint(expression="x >= 0"),
        ]
        problem = CVXPYProblem(
            variables=variables,
            objective=objective,
            constraints=constraints,
            description="Unbounded problem test"
        )

        result = solve_cvxpy_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status == "unbounded"

    def test_problem_validation(self):
        """Test problem validation."""
        # Empty variables
        problem = CVXPYProblem(
            variables=[],
            objective=CVXPYObjective(type=ObjectiveType.MINIMIZE, expression="0"),
            constraints=[],
            description="Invalid problem"
        )
        assert not problem.validate()

        # Missing objective
        problem = CVXPYProblem(
            variables=[CVXPYVariable(name="x", shape=1)],
            objective=None,  # This should cause validation to fail
            constraints=[],
            description="Invalid problem"
        )
        # Note: This test might need adjustment based on actual validation logic

    def test_variable_properties(self):
        """Test variable properties and constraints."""
        variables = [
            CVXPYVariable(
                name="x", 
                shape=2,
                nonneg=True,
                description="Non-negative variable"
            )
        ]
        objective = CVXPYObjective(
            type=ObjectiveType.MINIMIZE,
            expression="cp.sum(x)"
        )
        constraints = [
            CVXPYConstraint(expression="cp.sum(x) == 1"),
        ]
        problem = CVXPYProblem(
            variables=variables,
            objective=objective,
            constraints=constraints,
            description="Variable properties test"
        )

        result = solve_cvxpy_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status == "optimal"
        # Check that solution values are non-negative
        x_values = solution.values["x"]
        assert all(val >= 0 for val in x_values)

    def test_dual_values(self):
        """Test extraction of dual values."""
        variables = [CVXPYVariable(name="x", shape=1)]
        objective = CVXPYObjective(
            type=ObjectiveType.MINIMIZE,
            expression="x[0]"
        )
        constraints = [
            CVXPYConstraint(expression="x >= 0"),
            CVXPYConstraint(expression="x <= 1"),
        ]
        problem = CVXPYProblem(
            variables=variables,
            objective=objective,
            constraints=constraints,
            description="Dual values test"
        )

        result = solve_cvxpy_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status == "optimal"
        # Dual values might be available depending on solver
        if solution.dual_values:
            assert len(solution.dual_values) == len(constraints)
