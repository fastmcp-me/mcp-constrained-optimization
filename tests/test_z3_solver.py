"""
Tests for Z3 constraint satisfaction solver.
"""

import pytest
from returns.result import Success, Failure

from constrained_opt_mcp.models.z3_models import (
    Z3Problem, Z3Variable, Z3Constraint, Z3VariableType
)
from constrained_opt_mcp.solvers.z3_solver import solve_z3_problem


class TestZ3Solver:
    """Test cases for Z3 solver functionality."""

    def test_simple_arithmetic_constraints(self):
        """Test solving simple arithmetic constraints."""
        variables = [
            Z3Variable(name="x", type=Z3VariableType.INTEGER),
            Z3Variable(name="y", type=Z3VariableType.INTEGER),
        ]
        constraints = [
            Z3Constraint(expression="x + y == 10"),
            Z3Constraint(expression="x - y == 2"),
        ]
        problem = Z3Problem(
            variables=variables,
            constraints=constraints,
            description="Simple arithmetic problem"
        )

        result = solve_z3_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.is_satisfiable
        assert solution.values["x"] == 6
        assert solution.values["y"] == 4

    def test_boolean_constraints(self):
        """Test solving boolean constraint problems."""
        variables = [
            Z3Variable(name="a", type=Z3VariableType.BOOLEAN),
            Z3Variable(name="b", type=Z3VariableType.BOOLEAN),
        ]
        constraints = [
            Z3Constraint(expression="a == True"),
            Z3Constraint(expression="b == False"),
            Z3Constraint(expression="a != b"),
        ]
        problem = Z3Problem(
            variables=variables,
            constraints=constraints,
            description="Boolean constraint problem"
        )

        result = solve_z3_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.is_satisfiable
        assert solution.values["a"] is True
        assert solution.values["b"] is False

    def test_real_number_constraints(self):
        """Test solving real number constraints."""
        variables = [
            Z3Variable(name="x", type=Z3VariableType.REAL),
            Z3Variable(name="y", type=Z3VariableType.REAL),
        ]
        constraints = [
            Z3Constraint(expression="x + y == 5.5"),
            Z3Constraint(expression="x * y == 6.0"),
        ]
        problem = Z3Problem(
            variables=variables,
            constraints=constraints,
            description="Real number constraint problem"
        )

        result = solve_z3_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.is_satisfiable
        # Check that the solution satisfies the constraints
        x, y = solution.values["x"], solution.values["y"]
        assert abs(x + y - 5.5) < 1e-6
        assert abs(x * y - 6.0) < 1e-6

    def test_unsatisfiable_constraints(self):
        """Test handling of unsatisfiable constraints."""
        variables = [
            Z3Variable(name="x", type=Z3VariableType.INTEGER),
        ]
        constraints = [
            Z3Constraint(expression="x > 10"),
            Z3Constraint(expression="x < 5"),
        ]
        problem = Z3Problem(
            variables=variables,
            constraints=constraints,
            description="Unsatisfiable constraint problem"
        )

        result = solve_z3_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert not solution.is_satisfiable

    def test_variable_bounds(self):
        """Test solving with variable bounds."""
        variables = [
            Z3Variable(
                name="x", 
                type=Z3VariableType.INTEGER,
                lower_bound=0,
                upper_bound=10
            ),
        ]
        constraints = [
            Z3Constraint(expression="x > 5"),
        ]
        problem = Z3Problem(
            variables=variables,
            constraints=constraints,
            description="Bounded variable problem"
        )

        result = solve_z3_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.is_satisfiable
        assert 5 < solution.values["x"] <= 10

    def test_complex_logical_constraints(self):
        """Test solving complex logical constraints."""
        variables = [
            Z3Variable(name="p", type=Z3VariableType.BOOLEAN),
            Z3Variable(name="q", type=Z3VariableType.BOOLEAN),
            Z3Variable(name="r", type=Z3VariableType.BOOLEAN),
        ]
        constraints = [
            Z3Constraint(expression="p == True"),
            Z3Constraint(expression="Implies(p, q)"),
            Z3Constraint(expression="Implies(q, r)"),
            Z3Constraint(expression="r == True"),
        ]
        problem = Z3Problem(
            variables=variables,
            constraints=constraints,
            description="Complex logical constraint problem"
        )

        result = solve_z3_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.is_satisfiable
        assert solution.values["p"] is True
        assert solution.values["q"] is True
        assert solution.values["r"] is True

    def test_invalid_problem_validation(self):
        """Test problem validation."""
        # Empty variables
        problem = Z3Problem(
            variables=[],
            constraints=[Z3Constraint(expression="x == 1")],
            description="Invalid problem"
        )
        assert not problem.validate()

        # Empty constraints
        problem = Z3Problem(
            variables=[Z3Variable(name="x", type=Z3VariableType.INTEGER)],
            constraints=[],
            description="Invalid problem"
        )
        assert not problem.validate()

        # Duplicate variable names
        problem = Z3Problem(
            variables=[
                Z3Variable(name="x", type=Z3VariableType.INTEGER),
                Z3Variable(name="x", type=Z3VariableType.INTEGER),
            ],
            constraints=[Z3Constraint(expression="x == 1")],
            description="Invalid problem"
        )
        assert not problem.validate()

    def test_timeout_handling(self):
        """Test timeout handling."""
        variables = [
            Z3Variable(name="x", type=Z3VariableType.INTEGER),
        ]
        constraints = [
            Z3Constraint(expression="x > 0"),
        ]
        problem = Z3Problem(
            variables=variables,
            constraints=constraints,
            description="Timeout test problem",
            timeout=1  # 1ms timeout
        )

        result = solve_z3_problem(problem)
        # Should still succeed with timeout
        assert isinstance(result, Success)
