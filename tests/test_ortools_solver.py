"""
Tests for OR-Tools constraint programming solver.
"""

import pytest
from returns.result import Success, Failure

from constrained_opt_mcp.models.ortools_models import (
    ORToolsProblem, ORToolsVariable, ORToolsConstraint, ORToolsObjective,
    ORToolsVariableType, ORToolsObjectiveType
)
from constrained_opt_mcp.solvers.ortools_solver import solve_ortools_problem


class TestORToolsSolver:
    """Test cases for OR-Tools solver functionality."""

    def test_simple_boolean_problem(self):
        """Test solving simple boolean constraint problems."""
        variables = [
            ORToolsVariable(name="x", type=ORToolsVariableType.BOOLEAN),
            ORToolsVariable(name="y", type=ORToolsVariableType.BOOLEAN),
        ]
        constraints = [
            ORToolsConstraint(expression="model.add(x + y >= 1)"),
            ORToolsConstraint(expression="model.add(x != y)"),
        ]
        problem = ORToolsProblem(
            variables=variables,
            constraints=constraints,
            description="Simple boolean problem"
        )

        result = solve_ortools_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.is_feasible
        assert solution.values["x"] in [0, 1]
        assert solution.values["y"] in [0, 1]

    def test_integer_variable_problem(self):
        """Test solving problems with integer variables."""
        variables = [
            ORToolsVariable(
                name="x", 
                type=ORToolsVariableType.INTEGER,
                domain=(0, 10)
            ),
            ORToolsVariable(
                name="y", 
                type=ORToolsVariableType.INTEGER,
                domain=(0, 10)
            ),
        ]
        constraints = [
            ORToolsConstraint(expression="model.add(x + y == 10)"),
            ORToolsConstraint(expression="model.add(x - y >= 2)"),
        ]
        problem = ORToolsProblem(
            variables=variables,
            constraints=constraints,
            description="Integer variable problem"
        )

        result = solve_ortools_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.is_feasible
        assert solution.values["x"] + solution.values["y"] == 10
        assert solution.values["x"] - solution.values["y"] >= 2

    def test_optimization_problem(self):
        """Test solving optimization problems."""
        variables = [
            ORToolsVariable(
                name="x", 
                type=ORToolsVariableType.INTEGER,
                domain=(0, 10)
            ),
            ORToolsVariable(
                name="y", 
                type=ORToolsVariableType.INTEGER,
                domain=(0, 10)
            ),
        ]
        constraints = [
            ORToolsConstraint(expression="model.add(x + y <= 8)"),
            ORToolsConstraint(expression="model.add(x >= 1)"),
        ]
        objective = ORToolsObjective(
            type=ORToolsObjectiveType.MAXIMIZE,
            expression="x + y"
        )
        problem = ORToolsProblem(
            variables=variables,
            constraints=constraints,
            objective=objective,
            description="Optimization problem"
        )

        result = solve_ortools_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.is_feasible
        assert solution.objective_value is not None
        assert solution.objective_value == solution.values["x"] + solution.values["y"]

    def test_array_variables(self):
        """Test solving problems with array variables."""
        variables = [
            ORToolsVariable(
                name="x", 
                type=ORToolsVariableType.BOOLEAN,
                shape=[3, 3]
            ),
        ]
        constraints = [
            # Each row must have exactly one True
            ORToolsConstraint(expression="model.add(sum([x[i][j] for j in range(3)]) == 1 for i in range(3))"),
            # Each column must have exactly one True
            ORToolsConstraint(expression="model.add(sum([x[i][j] for i in range(3)]) == 1 for j in range(3))"),
        ]
        problem = ORToolsProblem(
            variables=variables,
            constraints=constraints,
            description="Array variables problem (3x3 Latin square)"
        )

        result = solve_ortools_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.is_feasible
        x_values = solution.values["x"]
        assert len(x_values) == 3
        assert len(x_values[0]) == 3

    def test_infeasible_problem(self):
        """Test handling of infeasible problems."""
        variables = [
            ORToolsVariable(
                name="x", 
                type=ORToolsVariableType.INTEGER,
                domain=(0, 5)
            ),
            ORToolsVariable(
                name="y", 
                type=ORToolsVariableType.INTEGER,
                domain=(0, 5)
            ),
        ]
        constraints = [
            ORToolsConstraint(expression="model.add(x + y == 20)"),  # Impossible with given domains
        ]
        problem = ORToolsProblem(
            variables=variables,
            constraints=constraints,
            description="Infeasible problem"
        )

        result = solve_ortools_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert not solution.is_feasible

    def test_soft_constraints(self):
        """Test solving problems with soft constraints."""
        variables = [
            ORToolsVariable(
                name="x", 
                type=ORToolsVariableType.INTEGER,
                domain=(0, 10)
            ),
        ]
        constraints = [
            ORToolsConstraint(
                expression="model.add(x >= 5)",
                is_soft=True,
                weight=1.0
            ),
            ORToolsConstraint(
                expression="model.add(x <= 3)",
                is_soft=True,
                weight=2.0
            ),
        ]
        problem = ORToolsProblem(
            variables=variables,
            constraints=constraints,
            description="Soft constraints problem"
        )

        result = solve_ortools_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        # Should find a solution even with conflicting soft constraints
        assert solution.is_feasible

    def test_interval_variables(self):
        """Test solving problems with interval variables."""
        variables = [
            ORToolsVariable(
                name="task", 
                type=ORToolsVariableType.INTERVAL,
                domain=(0, 10)
            ),
        ]
        constraints = [
            ORToolsConstraint(expression="model.add(task.start >= 0)"),
            ORToolsConstraint(expression="model.add(task.end <= 10)"),
        ]
        problem = ORToolsProblem(
            variables=variables,
            constraints=constraints,
            description="Interval variables problem"
        )

        result = solve_ortools_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.is_feasible

    def test_solver_parameters(self):
        """Test solving with custom solver parameters."""
        variables = [
            ORToolsVariable(
                name="x", 
                type=ORToolsVariableType.INTEGER,
                domain=(0, 100)
            ),
        ]
        constraints = [
            ORToolsConstraint(expression="model.add(x >= 10)"),
        ]
        parameters = {
            "max_time_in_seconds": 1.0,
            "log_search_progress": False,
        }
        problem = ORToolsProblem(
            variables=variables,
            constraints=constraints,
            parameters=parameters,
            description="Solver parameters test"
        )

        result = solve_ortools_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.is_feasible

    def test_problem_validation(self):
        """Test problem validation."""
        # Empty variables
        problem = ORToolsProblem(
            variables=[],
            constraints=[],
            description="Invalid problem"
        )
        assert not problem.validate()

        # Duplicate variable names
        variables = [
            ORToolsVariable(name="x", type=ORToolsVariableType.BOOLEAN),
            ORToolsVariable(name="x", type=ORToolsVariableType.BOOLEAN),
        ]
        problem = ORToolsProblem(
            variables=variables,
            constraints=[],
            description="Invalid problem"
        )
        assert not problem.validate()

    def test_statistics_extraction(self):
        """Test extraction of solver statistics."""
        variables = [
            ORToolsVariable(
                name="x", 
                type=ORToolsVariableType.INTEGER,
                domain=(0, 100)
            ),
        ]
        constraints = [
            ORToolsConstraint(expression="model.add(x >= 10)"),
            ORToolsConstraint(expression="model.add(x <= 50)"),
        ]
        problem = ORToolsProblem(
            variables=variables,
            constraints=constraints,
            description="Statistics test"
        )

        result = solve_ortools_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        assert solution.is_feasible
        assert solution.statistics is not None
        assert "num_conflicts" in solution.statistics
        assert "num_branches" in solution.statistics
        assert "wall_time" in solution.statistics

    def test_time_limit(self):
        """Test solving with time limit."""
        variables = [
            ORToolsVariable(
                name="x", 
                type=ORToolsVariableType.INTEGER,
                domain=(0, 1000)
            ),
        ]
        constraints = [
            ORToolsConstraint(expression="model.add(x >= 0)"),
        ]
        problem = ORToolsProblem(
            variables=variables,
            constraints=constraints,
            time_limit=0.001,  # Very short time limit
            description="Time limit test"
        )

        result = solve_ortools_problem(problem)
        assert isinstance(result, Success)
        
        solution = result.unwrap()
        # Should still find a solution even with time limit
        assert solution.is_feasible
