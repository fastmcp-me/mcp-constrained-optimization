"""
Tests for HiGHS linear and mixed-integer programming solver.
"""

import pytest
import numpy as np
from returns.result import Success, Failure

from constrained_opt_mcp.models.highs_models import (
    HiGHSProblem, HiGHSProblemSpec, HiGHSVariable, HiGHSConstraints,
    HiGHSObjective, HiGHSOptions, HiGHSSense, HiGHSVariableType,
    HiGHSConstraintSense
)
from constrained_opt_mcp.solvers.highs_solver import solve_highs_problem


class TestHiGHSSolver:
    """Test cases for HiGHS solver functionality."""

    def test_simple_linear_programming(self):
        """Test solving simple linear programming problems."""
        variables = [
            HiGHSVariable(name="x1", type=HiGHSVariableType.CONTINUOUS, lb=0, ub=10),
            HiGHSVariable(name="x2", type=HiGHSVariableType.CONTINUOUS, lb=0, ub=10),
        ]
        objective = HiGHSObjective(linear=[1.0, 2.0])
        constraints = HiGHSConstraints(
            dense=[[1, 1], [1, -1]],
            sense=[HiGHSConstraintSense.LESS_EQUAL, HiGHSConstraintSense.GREATER_EQUAL],
            rhs=[5.0, 1.0]
        )
        problem_spec = HiGHSProblemSpec(
            sense=HiGHSSense.MINIMIZE,
            objective=objective,
            variables=variables,
            constraints=constraints
        )
        problem = HiGHSProblem(problem=problem_spec)

        result = solve_highs_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status.value == "optimal"
        assert solution.objective_value is not None
        assert "x1" in solution.values
        assert "x2" in solution.values

    def test_mixed_integer_programming(self):
        """Test solving mixed-integer programming problems."""
        variables = [
            HiGHSVariable(name="x1", type=HiGHSVariableType.CONTINUOUS, lb=0, ub=10),
            HiGHSVariable(name="x2", type=HiGHSVariableType.INTEGER, lb=0, ub=10),
        ]
        objective = HiGHSObjective(linear=[1.0, 2.0])
        constraints = HiGHSConstraints(
            dense=[[1, 1], [1, -1]],
            sense=[HiGHSConstraintSense.LESS_EQUAL, HiGHSConstraintSense.GREATER_EQUAL],
            rhs=[5.0, 1.0]
        )
        problem_spec = HiGHSProblemSpec(
            sense=HiGHSSense.MINIMIZE,
            objective=objective,
            variables=variables,
            constraints=constraints
        )
        problem = HiGHSProblem(problem=problem_spec)

        result = solve_highs_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status.value == "optimal"
        # Check that x2 is integer
        assert solution.values["x2"] == int(solution.values["x2"])

    def test_binary_variables(self):
        """Test solving problems with binary variables."""
        variables = [
            HiGHSVariable(name="x1", type=HiGHSVariableType.BINARY),
            HiGHSVariable(name="x2", type=HiGHSVariableType.BINARY),
        ]
        objective = HiGHSObjective(linear=[1.0, 2.0])
        constraints = HiGHSConstraints(
            dense=[[1, 1]],
            sense=[HiGHSConstraintSense.LESS_EQUAL],
            rhs=[1.0]
        )
        problem_spec = HiGHSProblemSpec(
            sense=HiGHSSense.MAXIMIZE,
            objective=objective,
            variables=variables,
            constraints=constraints
        )
        problem = HiGHSProblem(problem=problem_spec)

        result = solve_highs_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status.value == "optimal"
        # Check that variables are binary
        assert solution.values["x1"] in [0, 1]
        assert solution.values["x2"] in [0, 1]

    def test_maximization_problem(self):
        """Test solving maximization problems."""
        variables = [
            HiGHSVariable(name="x1", type=HiGHSVariableType.CONTINUOUS, lb=0, ub=10),
            HiGHSVariable(name="x2", type=HiGHSVariableType.CONTINUOUS, lb=0, ub=10),
        ]
        objective = HiGHSObjective(linear=[3.0, 2.0])
        constraints = HiGHSConstraints(
            dense=[[1, 1], [2, 1]],
            sense=[HiGHSConstraintSense.LESS_EQUAL, HiGHSConstraintSense.LESS_EQUAL],
            rhs=[4.0, 6.0]
        )
        problem_spec = HiGHSProblemSpec(
            sense=HiGHSSense.MAXIMIZE,
            objective=objective,
            variables=variables,
            constraints=constraints
        )
        problem = HiGHSProblem(problem=problem_spec)

        result = solve_highs_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status.value == "optimal"
        assert solution.objective_value is not None

    def test_infeasible_problem(self):
        """Test handling of infeasible problems."""
        variables = [
            HiGHSVariable(name="x1", type=HiGHSVariableType.CONTINUOUS, lb=0, ub=10),
            HiGHSVariable(name="x2", type=HiGHSVariableType.CONTINUOUS, lb=0, ub=10),
        ]
        objective = HiGHSObjective(linear=[1.0, 1.0])
        constraints = HiGHSConstraints(
            dense=[[1, 1], [-1, -1]],
            sense=[HiGHSConstraintSense.LESS_EQUAL, HiGHSConstraintSense.LESS_EQUAL],
            rhs=[1.0, -2.0]  # This creates an infeasible problem
        )
        problem_spec = HiGHSProblemSpec(
            sense=HiGHSSense.MINIMIZE,
            objective=objective,
            variables=variables,
            constraints=constraints
        )
        problem = HiGHSProblem(problem=problem_spec)

        result = solve_highs_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status.value == "infeasible"

    def test_unbounded_problem(self):
        """Test handling of unbounded problems."""
        variables = [
            HiGHSVariable(name="x1", type=HiGHSVariableType.CONTINUOUS, lb=0),
            HiGHSVariable(name="x2", type=HiGHSVariableType.CONTINUOUS, lb=0),
        ]
        objective = HiGHSObjective(linear=[1.0, 1.0])
        constraints = HiGHSConstraints(
            dense=[[1, -1]],
            sense=[HiGHSConstraintSense.LESS_EQUAL],
            rhs=[0.0]
        )
        problem_spec = HiGHSProblemSpec(
            sense=HiGHSSense.MINIMIZE,
            objective=objective,
            variables=variables,
            constraints=constraints
        )
        problem = HiGHSProblem(problem=problem_spec)

        result = solve_highs_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status.value == "unbounded"

    def test_solver_options(self):
        """Test solver with custom options."""
        variables = [
            HiGHSVariable(name="x1", type=HiGHSVariableType.CONTINUOUS, lb=0, ub=10),
        ]
        objective = HiGHSObjective(linear=[1.0])
        constraints = HiGHSConstraints(
            dense=[[1]],
            sense=[HiGHSConstraintSense.LESS_EQUAL],
            rhs=[5.0]
        )
        problem_spec = HiGHSProblemSpec(
            sense=HiGHSSense.MINIMIZE,
            objective=objective,
            variables=variables,
            constraints=constraints
        )
        options = HiGHSOptions(
            time_limit=10.0,
            output_flag=False,
            presolve="on"
        )
        problem = HiGHSProblem(problem=problem_spec, options=options)

        result = solve_highs_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status.value == "optimal"

    def test_sparse_constraint_matrix(self):
        """Test solving with sparse constraint matrix."""
        variables = [
            HiGHSVariable(name="x1", type=HiGHSVariableType.CONTINUOUS, lb=0, ub=10),
            HiGHSVariable(name="x2", type=HiGHSVariableType.CONTINUOUS, lb=0, ub=10),
        ]
        objective = HiGHSObjective(linear=[1.0, 2.0])
        
        # Create sparse matrix
        from constrained_opt_mcp.models.highs_models import HiGHSSparseMatrix
        sparse_matrix = HiGHSSparseMatrix(
            rows=[0, 1],
            cols=[0, 1],
            values=[1.0, 1.0],
            shape=(2, 2)
        )
        
        constraints = HiGHSConstraints(
            dense=None,
            sparse=sparse_matrix,
            sense=[HiGHSConstraintSense.LESS_EQUAL, HiGHSConstraintSense.LESS_EQUAL],
            rhs=[5.0, 3.0]
        )
        problem_spec = HiGHSProblemSpec(
            sense=HiGHSSense.MINIMIZE,
            objective=objective,
            variables=variables,
            constraints=constraints
        )
        problem = HiGHSProblem(problem=problem_spec)

        result = solve_highs_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status.value == "optimal"

    def test_problem_validation(self):
        """Test problem validation."""
        # Empty variables
        problem_spec = HiGHSProblemSpec(
            sense=HiGHSSense.MINIMIZE,
            objective=HiGHSObjective(linear=[]),
            variables=[],
            constraints=HiGHSConstraints(dense=[], sense=[], rhs=[])
        )
        problem = HiGHSProblem(problem=problem_spec)
        assert not problem.validate()

        # Mismatched objective and variable dimensions
        variables = [HiGHSVariable(name="x1", type=HiGHSVariableType.CONTINUOUS)]
        objective = HiGHSObjective(linear=[1.0, 2.0])  # 2 coefficients for 1 variable
        constraints = HiGHSConstraints(dense=[], sense=[], rhs=[])
        problem_spec = HiGHSProblemSpec(
            sense=HiGHSSense.MINIMIZE,
            objective=objective,
            variables=variables,
            constraints=constraints
        )
        problem = HiGHSProblem(problem=problem_spec)
        # This should fail during solving, not validation

    def test_dual_values(self):
        """Test extraction of dual values."""
        variables = [
            HiGHSVariable(name="x1", type=HiGHSVariableType.CONTINUOUS, lb=0, ub=10),
            HiGHSVariable(name="x2", type=HiGHSVariableType.CONTINUOUS, lb=0, ub=10),
        ]
        objective = HiGHSObjective(linear=[1.0, 2.0])
        constraints = HiGHSConstraints(
            dense=[[1, 1], [1, -1]],
            sense=[HiGHSConstraintSense.LESS_EQUAL, HiGHSConstraintSense.GREATER_EQUAL],
            rhs=[5.0, 1.0]
        )
        problem_spec = HiGHSProblemSpec(
            sense=HiGHSSense.MINIMIZE,
            objective=objective,
            variables=variables,
            constraints=constraints
        )
        problem = HiGHSProblem(problem=problem_spec)

        result = solve_highs_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.status.value == "optimal"
        # Dual values should be available for linear programming
        if solution.dual_values:
            assert len(solution.dual_values) == len(constraints.sense)
