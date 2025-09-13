"""
Tests for MCP server tools.
"""

import pytest
import json
from unittest.mock import AsyncMock

from constrained_opt_mcp.server.main import (
    solve_constraint_satisfaction,
    solve_convex_optimization,
    solve_linear_programming,
    solve_constraint_programming,
    solve_portfolio_optimization,
)


class TestMCPServerTools:
    """Test cases for MCP server tool functionality."""

    @pytest.mark.asyncio
    async def test_solve_constraint_satisfaction(self):
        """Test constraint satisfaction tool."""
        variables = [
            {"name": "x", "type": "integer"},
            {"name": "y", "type": "integer"},
        ]
        constraints = [
            "x + y == 10",
            "x - y == 2",
        ]
        
        result = await solve_constraint_satisfaction(
            variables=variables,
            constraints=constraints,
            description="Test problem"
        )
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        data = json.loads(result[0].text)
        assert data["is_satisfiable"]
        assert data["values"]["x"] == 6
        assert data["values"]["y"] == 4

    @pytest.mark.asyncio
    async def test_solve_convex_optimization(self):
        """Test convex optimization tool."""
        variables = [{"name": "x", "shape": 2}]
        objective_type = "minimize"
        objective_expr = "cp.sum_squares(x)"
        constraints = [
            "x >= 0",
            "cp.sum(x) == 1",
        ]
        
        result = await solve_convex_optimization(
            variables=variables,
            objective_type=objective_type,
            objective_expr=objective_expr,
            constraints=constraints,
            description="Test convex problem"
        )
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        data = json.loads(result[0].text)
        assert data["status"] == "optimal"
        assert "values" in data
        assert "objective_value" in data

    @pytest.mark.asyncio
    async def test_solve_linear_programming(self):
        """Test linear programming tool."""
        sense = "minimize"
        objective_coeffs = [1.0, 2.0]
        variables = [
            {"name": "x1", "lb": 0, "ub": 10, "type": "cont"},
            {"name": "x2", "lb": 0, "ub": 10, "type": "cont"},
        ]
        constraint_matrix = [[1, 1], [1, -1]]
        constraint_senses = ["<=", ">="]
        rhs_values = [5.0, 1.0]
        
        result = await solve_linear_programming(
            sense=sense,
            objective_coeffs=objective_coeffs,
            variables=variables,
            constraint_matrix=constraint_matrix,
            constraint_senses=constraint_senses,
            rhs_values=rhs_values,
            description="Test LP problem"
        )
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        data = json.loads(result[0].text)
        assert data["status"] == "optimal"
        assert "values" in data
        assert "objective_value" in data

    @pytest.mark.asyncio
    async def test_solve_constraint_programming(self):
        """Test constraint programming tool."""
        variables = [
            {"name": "x", "type": "integer", "domain": [0, 10]},
            {"name": "y", "type": "integer", "domain": [0, 10]},
        ]
        constraints = [
            "model.add(x + y == 10)",
            "model.add(x - y >= 2)",
        ]
        objective = {
            "type": "minimize",
            "expression": "x + y"
        }
        
        result = await solve_constraint_programming(
            variables=variables,
            constraints=constraints,
            objective=objective,
            description="Test CP problem"
        )
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        data = json.loads(result[0].text)
        assert data["is_feasible"]
        assert "values" in data

    @pytest.mark.asyncio
    async def test_solve_portfolio_optimization(self):
        """Test portfolio optimization tool."""
        assets = ["Bonds", "Stocks", "RealEstate", "Commodities"]
        expected_returns = [0.08, 0.12, 0.10, 0.15]
        risk_factors = [0.02, 0.15, 0.08, 0.20]
        correlation_matrix = [
            [1.0, 0.2, 0.3, 0.1],
            [0.2, 1.0, 0.6, 0.7],
            [0.3, 0.6, 1.0, 0.5],
            [0.1, 0.7, 0.5, 1.0],
        ]
        max_allocations = [0.4, 0.6, 0.3, 0.2]
        risk_budget = 0.01
        
        result = await solve_portfolio_optimization(
            assets=assets,
            expected_returns=expected_returns,
            risk_factors=risk_factors,
            correlation_matrix=correlation_matrix,
            max_allocations=max_allocations,
            risk_budget=risk_budget,
            description="Test portfolio optimization"
        )
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        data = json.loads(result[0].text)
        assert data["status"] == "optimal"
        assert "weights" in data
        assert "expected_return" in data
        assert "portfolio_risk" in data
        assert "sharpe_ratio" in data

    @pytest.mark.asyncio
    async def test_invalid_variable_types(self):
        """Test handling of invalid variable types."""
        variables = [
            {"name": "x", "type": "invalid_type"},
        ]
        constraints = ["x == 1"]
        
        result = await solve_constraint_satisfaction(
            variables=variables,
            constraints=constraints
        )
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Invalid variable type" in result[0].text

    @pytest.mark.asyncio
    async def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        variables = [
            {"name": "x"},  # Missing type field
        ]
        constraints = ["x == 1"]
        
        result = await solve_constraint_satisfaction(
            variables=variables,
            constraints=constraints
        )
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "must have 'name' and 'type' fields" in result[0].text

    @pytest.mark.asyncio
    async def test_invalid_objective_type(self):
        """Test handling of invalid objective types."""
        variables = [{"name": "x", "shape": 1}]
        objective_type = "invalid_type"
        objective_expr = "x[0]"
        constraints = ["x >= 0"]
        
        result = await solve_convex_optimization(
            variables=variables,
            objective_type=objective_type,
            objective_expr=objective_expr,
            constraints=constraints
        )
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Invalid objective type" in result[0].text

    @pytest.mark.asyncio
    async def test_invalid_sense(self):
        """Test handling of invalid optimization sense."""
        sense = "invalid_sense"
        objective_coeffs = [1.0]
        variables = [{"name": "x1", "type": "cont"}]
        constraint_matrix = []
        constraint_senses = []
        rhs_values = []
        
        result = await solve_linear_programming(
            sense=sense,
            objective_coeffs=objective_coeffs,
            variables=variables,
            constraint_matrix=constraint_matrix,
            constraint_senses=constraint_senses,
            rhs_values=rhs_values
        )
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Invalid sense" in result[0].text

    @pytest.mark.asyncio
    async def test_portfolio_optimization_validation(self):
        """Test portfolio optimization input validation."""
        # Mismatched array lengths
        assets = ["A", "B"]
        expected_returns = [0.1, 0.2, 0.3]  # Wrong length
        risk_factors = [0.05, 0.1]
        correlation_matrix = [[1.0, 0.5], [0.5, 1.0]]
        
        result = await solve_portfolio_optimization(
            assets=assets,
            expected_returns=expected_returns,
            risk_factors=risk_factors,
            correlation_matrix=correlation_matrix
        )
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "length must match" in result[0].text

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test general error handling."""
        # This should trigger an exception in the solver
        variables = [{"name": "x", "type": "integer"}]
        constraints = ["invalid_syntax_here"]
        
        result = await solve_constraint_satisfaction(
            variables=variables,
            constraints=constraints
        )
        
        assert len(result) == 1
        assert result[0].type == "text"
        # Should return an error message, not crash
        assert "Error" in result[0].text
