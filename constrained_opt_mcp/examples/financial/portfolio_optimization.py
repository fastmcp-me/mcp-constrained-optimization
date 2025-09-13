"""
Advanced Portfolio Optimization Examples

This module demonstrates various portfolio optimization strategies using the
constrained optimization MCP server, including:

1. Modern Portfolio Theory (Markowitz)
2. Risk Parity Portfolio
3. Black-Litterman Model
4. Factor-based Portfolio Construction
5. ESG-constrained Portfolio Optimization
6. Multi-period Portfolio Optimization
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import json

from ...server.main import solve_portfolio_optimization, solve_convex_optimization


class PortfolioOptimizer:
    """Advanced portfolio optimization using the MCP server."""
    
    def __init__(self, assets: List[str], expected_returns: List[float], 
                 risk_factors: List[float], correlation_matrix: List[List[float]]):
        """
        Initialize portfolio optimizer.
        
        Args:
            assets: List of asset names
            expected_returns: Expected returns for each asset
            risk_factors: Risk factors (standard deviations) for each asset
            correlation_matrix: Correlation matrix between assets
        """
        self.assets = assets
        self.expected_returns = np.array(expected_returns)
        self.risk_factors = np.array(risk_factors)
        self.correlation_matrix = np.array(correlation_matrix)
        self.n_assets = len(assets)
        
        # Validate inputs
        self._validate_inputs()
        
        # Create covariance matrix
        self.covariance_matrix = np.outer(self.risk_factors, self.risk_factors) * self.correlation_matrix
    
    def _validate_inputs(self):
        """Validate input parameters."""
        assert len(self.expected_returns) == self.n_assets, "Expected returns length mismatch"
        assert len(self.risk_factors) == self.n_assets, "Risk factors length mismatch"
        assert self.correlation_matrix.shape == (self.n_assets, self.n_assets), "Correlation matrix shape mismatch"
        
        # Check correlation matrix is symmetric and positive definite
        assert np.allclose(self.correlation_matrix, self.correlation_matrix.T), "Correlation matrix not symmetric"
        assert np.all(np.linalg.eigvals(self.correlation_matrix) > 0), "Correlation matrix not positive definite"
    
    def markowitz_optimization(self, risk_budget: float = 0.01, 
                              max_allocations: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Solve Markowitz mean-variance optimization problem.
        
        Args:
            risk_budget: Maximum portfolio variance
            max_allocations: Maximum allocation for each asset
            
        Returns:
            Dictionary with optimal weights and performance metrics
        """
        if max_allocations is None:
            max_allocations = [1.0] * self.n_assets
        
        # Use the MCP server to solve
        result = solve_portfolio_optimization(
            assets=self.assets,
            expected_returns=self.expected_returns.tolist(),
            risk_factors=self.risk_factors.tolist(),
            correlation_matrix=self.correlation_matrix.tolist(),
            max_allocations=max_allocations,
            risk_budget=risk_budget,
            description="Markowitz mean-variance optimization"
        )
        
        if result and len(result) > 0:
            data = json.loads(result[0].text)
            return data
        else:
            raise RuntimeError("Portfolio optimization failed")
    
    def risk_parity_optimization(self) -> Dict[str, Any]:
        """
        Solve risk parity optimization problem.
        
        Risk parity aims to equalize the risk contribution of each asset.
        
        Returns:
            Dictionary with optimal weights and performance metrics
        """
        # Risk parity can be formulated as a convex optimization problem
        # Minimize sum of squared risk contributions
        
        variables = [{"name": "weights", "shape": self.n_assets}]
        objective_type = "minimize"
        
        # Risk parity objective: minimize sum of squared risk contributions
        # This is a quadratic form: w^T * Sigma * w, but we want to equalize contributions
        # We can use a proxy: minimize the variance of risk contributions
        objective_expr = "cp.sum_squares(cp.multiply(weights, cp.sqrt(cp.diag(covariance_matrix))))"
        
        constraints = [
            "cp.sum(weights) == 1",
            "weights >= 0",
        ]
        
        parameters = {
            "covariance_matrix": self.covariance_matrix,
        }
        
        result = solve_convex_optimization(
            variables=variables,
            objective_type=objective_type,
            objective_expr=objective_expr,
            constraints=constraints,
            parameters=parameters,
            description="Risk parity portfolio optimization"
        )
        
        if result and len(result) > 0:
            data = json.loads(result[0].text)
            return data
        else:
            raise RuntimeError("Risk parity optimization failed")
    
    def black_litterman_optimization(self, market_caps: List[float], 
                                   risk_aversion: float = 3.0,
                                   tau: float = 0.05) -> Dict[str, Any]:
        """
        Solve Black-Litterman optimization problem.
        
        Args:
            market_caps: Market capitalizations for each asset
            risk_aversion: Risk aversion parameter
            tau: Confidence parameter for views
            
        Returns:
            Dictionary with optimal weights and performance metrics
        """
        # Black-Litterman model combines market equilibrium with investor views
        # Market implied returns: Pi = lambda * Sigma * w_market
        market_caps = np.array(market_caps)
        w_market = market_caps / np.sum(market_caps)
        
        # Market implied returns
        pi = risk_aversion * self.covariance_matrix @ w_market
        
        # Black-Litterman expected returns
        # For simplicity, we'll use the market implied returns
        # In practice, you would incorporate investor views here
        
        # Solve optimization with BL expected returns
        result = solve_portfolio_optimization(
            assets=self.assets,
            expected_returns=pi.tolist(),
            risk_factors=self.risk_factors.tolist(),
            correlation_matrix=self.correlation_matrix.tolist(),
            description="Black-Litterman portfolio optimization"
        )
        
        if result and len(result) > 0:
            data = json.loads(result[0].text)
            return data
        else:
            raise RuntimeError("Black-Litterman optimization failed")
    
    def esg_constrained_optimization(self, esg_scores: List[float], 
                                   min_esg_score: float = 0.6) -> Dict[str, Any]:
        """
        Solve ESG-constrained portfolio optimization.
        
        Args:
            esg_scores: ESG scores for each asset (0-1 scale)
            min_esg_score: Minimum average ESG score for portfolio
            
        Returns:
            Dictionary with optimal weights and performance metrics
        """
        esg_scores = np.array(esg_scores)
        
        # Use CVXPY for ESG constraints
        variables = [{"name": "weights", "shape": self.n_assets}]
        objective_type = "maximize"
        objective_expr = "expected_returns.T @ weights"
        
        constraints = [
            "cp.sum(weights) == 1",
            "weights >= 0",
            f"esg_scores.T @ weights >= {min_esg_score}",  # ESG constraint
        ]
        
        parameters = {
            "expected_returns": self.expected_returns,
            "esg_scores": esg_scores,
        }
        
        result = solve_convex_optimization(
            variables=variables,
            objective_type=objective_type,
            objective_expr=objective_expr,
            constraints=constraints,
            parameters=parameters,
            description="ESG-constrained portfolio optimization"
        )
        
        if result and len(result) > 0:
            data = json.loads(result[0].text)
            return data
        else:
            raise RuntimeError("ESG-constrained optimization failed")
    
    def factor_based_optimization(self, factor_loadings: np.ndarray, 
                                factor_returns: List[float],
                                factor_covariance: np.ndarray) -> Dict[str, Any]:
        """
        Solve factor-based portfolio optimization.
        
        Args:
            factor_loadings: Factor loadings matrix (assets x factors)
            factor_returns: Expected factor returns
            factor_covariance: Factor covariance matrix
            
        Returns:
            Dictionary with optimal weights and performance metrics
        """
        # Factor model: R = alpha + B * F + epsilon
        # Portfolio return: w^T * R = w^T * alpha + w^T * B * F + w^T * epsilon
        # Portfolio variance: w^T * B * Sigma_F * B^T * w + w^T * Sigma_epsilon * w
        
        n_factors = len(factor_returns)
        factor_loadings = np.array(factor_loadings)
        factor_returns = np.array(factor_returns)
        factor_covariance = np.array(factor_covariance)
        
        # Calculate factor-based expected returns and covariance
        factor_expected_returns = factor_loadings @ factor_returns
        factor_covariance_matrix = factor_loadings @ factor_covariance @ factor_loadings.T
        
        # Add idiosyncratic risk (simplified)
        idiosyncratic_risk = np.diag(self.risk_factors**2) * 0.1  # 10% idiosyncratic
        total_covariance = factor_covariance_matrix + idiosyncratic_risk
        
        # Convert to correlation matrix
        std_devs = np.sqrt(np.diag(total_covariance))
        correlation_matrix = total_covariance / np.outer(std_devs, std_devs)
        
        result = solve_portfolio_optimization(
            assets=self.assets,
            expected_returns=factor_expected_returns.tolist(),
            risk_factors=std_devs.tolist(),
            correlation_matrix=correlation_matrix.tolist(),
            description="Factor-based portfolio optimization"
        )
        
        if result and len(result) > 0:
            data = json.loads(result[0].text)
            return data
        else:
            raise RuntimeError("Factor-based optimization failed")
    
    def multi_period_optimization(self, time_horizon: int = 12,
                                 rebalancing_cost: float = 0.001) -> Dict[str, Any]:
        """
        Solve multi-period portfolio optimization with transaction costs.
        
        Args:
            time_horizon: Number of periods
            rebalancing_cost: Transaction cost per rebalancing
            
        Returns:
            Dictionary with optimal weights and performance metrics
        """
        # This is a simplified multi-period model
        # In practice, you would use dynamic programming or stochastic optimization
        
        # For now, we'll solve a single-period problem with transaction cost penalty
        variables = [{"name": "weights", "shape": self.n_assets}]
        objective_type = "maximize"
        
        # Objective: maximize expected return minus transaction cost penalty
        objective_expr = "expected_returns.T @ weights - rebalancing_cost * cp.sum(cp.abs(weights - initial_weights))"
        
        constraints = [
            "cp.sum(weights) == 1",
            "weights >= 0",
        ]
        
        # Assume equal initial weights
        initial_weights = np.ones(self.n_assets) / self.n_assets
        
        parameters = {
            "expected_returns": self.expected_returns,
            "rebalancing_cost": rebalancing_cost,
            "initial_weights": initial_weights,
        }
        
        result = solve_convex_optimization(
            variables=variables,
            objective_type=objective_type,
            objective_expr=objective_expr,
            constraints=constraints,
            parameters=parameters,
            description="Multi-period portfolio optimization with transaction costs"
        )
        
        if result and len(result) > 0:
            data = json.loads(result[0].text)
            return data
        else:
            raise RuntimeError("Multi-period optimization failed")


def create_sample_portfolio_data() -> Tuple[List[str], List[float], List[float], List[List[float]]]:
    """Create sample portfolio data for testing."""
    assets = [
        "US_Stocks", "International_Stocks", "US_Bonds", "International_Bonds",
        "Real_Estate", "Commodities", "Emerging_Markets", "Cash"
    ]
    
    expected_returns = [0.10, 0.08, 0.03, 0.02, 0.07, 0.06, 0.12, 0.01]
    risk_factors = [0.15, 0.18, 0.03, 0.05, 0.12, 0.20, 0.25, 0.01]
    
    # Realistic correlation matrix
    correlation_matrix = [
        [1.00, 0.70, 0.20, 0.15, 0.60, 0.30, 0.65, 0.00],
        [0.70, 1.00, 0.10, 0.25, 0.50, 0.40, 0.80, 0.00],
        [0.20, 0.10, 1.00, 0.60, 0.15, 0.05, 0.10, 0.00],
        [0.15, 0.25, 0.60, 1.00, 0.20, 0.10, 0.20, 0.00],
        [0.60, 0.50, 0.15, 0.20, 1.00, 0.25, 0.55, 0.00],
        [0.30, 0.40, 0.05, 0.10, 0.25, 1.00, 0.45, 0.00],
        [0.65, 0.80, 0.10, 0.20, 0.55, 0.45, 1.00, 0.00],
        [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00],
    ]
    
    return assets, expected_returns, risk_factors, correlation_matrix


def main():
    """Demonstrate portfolio optimization examples."""
    print("Portfolio Optimization Examples")
    print("=" * 50)
    
    # Create sample data
    assets, expected_returns, risk_factors, correlation_matrix = create_sample_portfolio_data()
    
    # Initialize optimizer
    optimizer = PortfolioOptimizer(assets, expected_returns, risk_factors, correlation_matrix)
    
    print("\n1. Markowitz Mean-Variance Optimization")
    print("-" * 40)
    try:
        result = optimizer.markowitz_optimization(risk_budget=0.01)
        print(f"Status: {result['status']}")
        print("Optimal Weights:")
        for asset, weight in result['weights'].items():
            print(f"  {asset}: {weight:.1%}")
        print(f"Expected Return: {result['expected_return']:.1%}")
        print(f"Portfolio Risk: {result['portfolio_risk']:.1%}")
        print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n2. ESG-Constrained Optimization")
    print("-" * 40)
    try:
        esg_scores = [0.8, 0.7, 0.9, 0.8, 0.6, 0.5, 0.4, 1.0]  # Cash has perfect ESG score
        result = optimizer.esg_constrained_optimization(esg_scores, min_esg_score=0.7)
        print(f"Status: {result['status']}")
        print("Optimal Weights:")
        for asset, weight in result['weights'].items():
            print(f"  {asset}: {weight:.1%}")
        print(f"Expected Return: {result['objective_value']:.1%}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n3. Black-Litterman Optimization")
    print("-" * 40)
    try:
        market_caps = [0.4, 0.3, 0.15, 0.1, 0.03, 0.01, 0.005, 0.005]  # Market cap weights
        result = optimizer.black_litterman_optimization(market_caps)
        print(f"Status: {result['status']}")
        print("Optimal Weights:")
        for asset, weight in result['weights'].items():
            print(f"  {asset}: {weight:.1%}")
        print(f"Expected Return: {result['expected_return']:.1%}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
