"""
Risk Management and Hedging Examples

This module demonstrates various risk management strategies using the
constrained optimization MCP server, including:

1. Value-at-Risk (VaR) Optimization
2. Conditional Value-at-Risk (CVaR) Optimization
3. Portfolio Hedging Strategies
4. Stress Testing and Scenario Analysis
5. Risk Budgeting
6. Dynamic Hedging with Options
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import json
from scipy import stats

from ...server.main import solve_convex_optimization, solve_linear_programming


class RiskManager:
    """Advanced risk management using the MCP server."""
    
    def __init__(self, assets: List[str], returns_data: np.ndarray):
        """
        Initialize risk manager.
        
        Args:
            assets: List of asset names
            returns_data: Historical returns data (time_series x assets)
        """
        self.assets = assets
        self.returns_data = returns_data
        self.n_assets = len(assets)
        self.n_periods = returns_data.shape[0]
        
        # Calculate statistics
        self.expected_returns = np.mean(returns_data, axis=0)
        self.covariance_matrix = np.cov(returns_data.T)
        self.correlation_matrix = self._correlation_from_covariance(self.covariance_matrix)
    
    def _correlation_from_covariance(self, cov_matrix: np.ndarray) -> np.ndarray:
        """Convert covariance matrix to correlation matrix."""
        std_devs = np.sqrt(np.diag(cov_matrix))
        return cov_matrix / np.outer(std_devs, std_devs)
    
    def var_optimization(self, confidence_level: float = 0.05,
                        max_var: float = 0.02) -> Dict[str, Any]:
        """
        Optimize portfolio to minimize Value-at-Risk.
        
        Args:
            confidence_level: VaR confidence level (e.g., 0.05 for 5% VaR)
            max_var: Maximum allowed VaR
            
        Returns:
            Dictionary with optimal weights and VaR metrics
        """
        # VaR optimization using historical simulation
        # For normal distribution: VaR = -μ + σ * z_α
        # where z_α is the α-quantile of standard normal distribution
        
        z_alpha = stats.norm.ppf(confidence_level)
        
        # Use CVXPY for VaR optimization
        variables = [{"name": "weights", "shape": self.n_assets}]
        objective_type = "maximize"
        objective_expr = "expected_returns.T @ weights"  # Maximize expected return
        
        constraints = [
            "cp.sum(weights) == 1",
            "weights >= 0",
            f"expected_returns.T @ weights - z_alpha * cp.sqrt(cp.quad_form(weights, covariance_matrix)) >= -{max_var}",
        ]
        
        parameters = {
            "expected_returns": self.expected_returns,
            "covariance_matrix": self.covariance_matrix,
        }
        
        result = solve_convex_optimization(
            variables=variables,
            objective_type=objective_type,
            objective_expr=objective_expr,
            constraints=constraints,
            parameters=parameters,
            description=f"VaR optimization with {confidence_level:.1%} confidence level"
        )
        
        if result and len(result) > 0:
            data = json.loads(result[0].text)
            return data
        else:
            raise RuntimeError("VaR optimization failed")
    
    def cvar_optimization(self, confidence_level: float = 0.05,
                         max_cvar: float = 0.03) -> Dict[str, Any]:
        """
        Optimize portfolio to minimize Conditional Value-at-Risk (CVaR).
        
        Args:
            confidence_level: CVaR confidence level
            max_cvar: Maximum allowed CVaR
            
        Returns:
            Dictionary with optimal weights and CVaR metrics
        """
        # CVaR optimization using historical simulation
        # CVaR is the expected loss beyond VaR
        
        # For normal distribution: CVaR = -μ + σ * φ(z_α) / α
        # where φ is the standard normal density function
        
        z_alpha = stats.norm.ppf(confidence_level)
        phi_z_alpha = stats.norm.pdf(z_alpha)
        cvar_factor = phi_z_alpha / confidence_level
        
        variables = [{"name": "weights", "shape": self.n_assets}]
        objective_type = "maximize"
        objective_expr = "expected_returns.T @ weights"
        
        constraints = [
            "cp.sum(weights) == 1",
            "weights >= 0",
            f"expected_returns.T @ weights - cvar_factor * cp.sqrt(cp.quad_form(weights, covariance_matrix)) >= -{max_cvar}",
        ]
        
        parameters = {
            "expected_returns": self.expected_returns,
            "covariance_matrix": self.covariance_matrix,
            "cvar_factor": cvar_factor,
        }
        
        result = solve_convex_optimization(
            variables=variables,
            objective_type=objective_type,
            objective_expr=objective_expr,
            constraints=constraints,
            parameters=parameters,
            description=f"CVaR optimization with {confidence_level:.1%} confidence level"
        )
        
        if result and len(result) > 0:
            data = json.loads(result[0].text)
            return data
        else:
            raise RuntimeError("CVaR optimization failed")
    
    def portfolio_hedging(self, hedge_assets: List[str], 
                         hedge_ratios: List[float],
                         max_hedge_cost: float = 0.1) -> Dict[str, Any]:
        """
        Optimize portfolio hedging strategy.
        
        Args:
            hedge_assets: Assets available for hedging
            hedge_ratios: Hedge ratios for each asset
            max_hedge_cost: Maximum cost of hedging
            
        Returns:
            Dictionary with optimal hedging strategy
        """
        # Find indices of hedge assets
        hedge_indices = [self.assets.index(asset) for asset in hedge_assets]
        hedge_ratios = np.array(hedge_ratios)
        
        # Create hedging variables
        variables = [
            {"name": "portfolio_weights", "shape": self.n_assets},
            {"name": "hedge_weights", "shape": len(hedge_assets)},
        ]
        
        objective_type = "maximize"
        # Maximize expected return minus hedging cost
        objective_expr = "expected_returns.T @ portfolio_weights - cp.sum(cp.multiply(hedge_weights, hedge_costs))"
        
        constraints = [
            "cp.sum(portfolio_weights) == 1",
            "portfolio_weights >= 0",
            "hedge_weights >= 0",
            f"cp.sum(cp.multiply(hedge_weights, hedge_costs)) <= {max_hedge_cost}",
            # Hedging constraint: reduce portfolio risk
            "cp.quad_form(portfolio_weights, covariance_matrix) <= original_risk * (1 - cp.sum(hedge_weights))",
        ]
        
        # Calculate original portfolio risk (equal weights)
        original_weights = np.ones(self.n_assets) / self.n_assets
        original_risk = original_weights.T @ self.covariance_matrix @ original_weights
        
        # Assume hedging costs are proportional to hedge ratios
        hedge_costs = hedge_ratios * 0.01  # 1% cost per unit hedge ratio
        
        parameters = {
            "expected_returns": self.expected_returns,
            "covariance_matrix": self.covariance_matrix,
            "hedge_costs": hedge_costs,
            "original_risk": original_risk,
        }
        
        result = solve_convex_optimization(
            variables=variables,
            objective_type=objective_type,
            objective_expr=objective_expr,
            constraints=constraints,
            parameters=parameters,
            description="Portfolio hedging optimization"
        )
        
        if result and len(result) > 0:
            data = json.loads(result[0].text)
            return data
        else:
            raise RuntimeError("Portfolio hedging optimization failed")
    
    def stress_testing(self, stress_scenarios: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Perform stress testing on portfolio.
        
        Args:
            stress_scenarios: List of stress scenarios with asset returns
            
        Returns:
            Dictionary with stress test results
        """
        results = {}
        
        for i, scenario in enumerate(stress_scenarios):
            scenario_name = scenario.get("name", f"Scenario_{i+1}")
            scenario_returns = np.array([scenario[asset] for asset in self.assets])
            
            # Calculate portfolio performance under stress
            # Assume equal weights for simplicity
            equal_weights = np.ones(self.n_assets) / self.n_assets
            portfolio_return = np.sum(equal_weights * scenario_returns)
            
            # Calculate portfolio variance under stress
            # Use historical covariance as proxy
            portfolio_variance = equal_weights.T @ self.covariance_matrix @ equal_weights
            portfolio_volatility = np.sqrt(portfolio_variance)
            
            results[scenario_name] = {
                "portfolio_return": portfolio_return,
                "portfolio_volatility": portfolio_volatility,
                "sharpe_ratio": portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0,
                "scenario_returns": dict(zip(self.assets, scenario_returns)),
            }
        
        return results
    
    def risk_budgeting(self, risk_budgets: List[float]) -> Dict[str, Any]:
        """
        Optimize portfolio using risk budgeting approach.
        
        Args:
            risk_budgets: Target risk budget for each asset
            
        Returns:
            Dictionary with optimal weights and risk contributions
        """
        risk_budgets = np.array(risk_budgets)
        risk_budgets = risk_budgets / np.sum(risk_budgets)  # Normalize to sum to 1
        
        # Risk budgeting: minimize sum of squared differences between
        # actual risk contributions and target risk budgets
        
        variables = [{"name": "weights", "shape": self.n_assets}]
        objective_type = "minimize"
        
        # Risk contribution of asset i: w_i * (Sigma * w)_i / (w^T * Sigma * w)
        # We want to minimize the sum of squared differences
        objective_expr = "cp.sum_squares(cp.multiply(weights, cp.matmul(covariance_matrix, weights)) / cp.quad_form(weights, covariance_matrix) - risk_budgets)"
        
        constraints = [
            "cp.sum(weights) == 1",
            "weights >= 0",
        ]
        
        parameters = {
            "covariance_matrix": self.covariance_matrix,
            "risk_budgets": risk_budgets,
        }
        
        result = solve_convex_optimization(
            variables=variables,
            objective_type=objective_type,
            objective_expr=objective_expr,
            constraints=constraints,
            parameters=parameters,
            description="Risk budgeting optimization"
        )
        
        if result and len(result) > 0:
            data = json.loads(result[0].text)
            return data
        else:
            raise RuntimeError("Risk budgeting optimization failed")
    
    def dynamic_hedging_options(self, option_prices: List[float],
                               option_deltas: List[float],
                               option_gammas: List[float]) -> Dict[str, Any]:
        """
        Optimize dynamic hedging strategy using options.
        
        Args:
            option_prices: Option prices for hedging
            option_deltas: Option deltas for hedging
            option_gammas: Option gammas for hedging
            
        Returns:
            Dictionary with optimal hedging strategy
        """
        # Dynamic hedging with options
        # Minimize portfolio variance while considering option costs
        
        n_options = len(option_prices)
        
        variables = [
            {"name": "portfolio_weights", "shape": self.n_assets},
            {"name": "option_weights", "shape": n_options},
        ]
        
        objective_type = "minimize"
        # Minimize portfolio variance plus option costs
        objective_expr = "cp.quad_form(portfolio_weights, covariance_matrix) + cp.sum(cp.multiply(option_weights, option_prices))"
        
        constraints = [
            "cp.sum(portfolio_weights) == 1",
            "portfolio_weights >= 0",
            "option_weights >= 0",
            # Delta hedging constraint
            "cp.sum(cp.multiply(option_weights, option_deltas)) == 0",
            # Gamma hedging constraint (optional)
            "cp.sum(cp.multiply(option_weights, option_gammas)) <= 0.1",
        ]
        
        parameters = {
            "covariance_matrix": self.covariance_matrix,
            "option_prices": np.array(option_prices),
            "option_deltas": np.array(option_deltas),
            "option_gammas": np.array(option_gammas),
        }
        
        result = solve_convex_optimization(
            variables=variables,
            objective_type=objective_type,
            objective_expr=objective_expr,
            constraints=constraints,
            parameters=parameters,
            description="Dynamic hedging with options"
        )
        
        if result and len(result) > 0:
            data = json.loads(result[0].text)
            return data
        else:
            raise RuntimeError("Dynamic hedging optimization failed")


def create_sample_risk_data() -> Tuple[List[str], np.ndarray]:
    """Create sample risk management data for testing."""
    assets = ["US_Stocks", "International_Stocks", "US_Bonds", "Commodities"]
    
    # Generate sample returns data (252 trading days)
    np.random.seed(42)
    n_days = 252
    n_assets = len(assets)
    
    # Create realistic returns with different volatilities
    expected_returns = np.array([0.10, 0.08, 0.03, 0.06])
    volatilities = np.array([0.15, 0.18, 0.03, 0.20])
    
    # Generate correlated returns
    correlation_matrix = np.array([
        [1.0, 0.7, 0.2, 0.3],
        [0.7, 1.0, 0.1, 0.4],
        [0.2, 0.1, 1.0, 0.05],
        [0.3, 0.4, 0.05, 1.0],
    ])
    
    # Generate multivariate normal returns
    cov_matrix = np.outer(volatilities, volatilities) * correlation_matrix
    returns_data = np.random.multivariate_normal(expected_returns, cov_matrix, n_days)
    
    return assets, returns_data


def main():
    """Demonstrate risk management examples."""
    print("Risk Management Examples")
    print("=" * 50)
    
    # Create sample data
    assets, returns_data = create_sample_risk_data()
    
    # Initialize risk manager
    risk_manager = RiskManager(assets, returns_data)
    
    print("\n1. Value-at-Risk Optimization")
    print("-" * 40)
    try:
        result = risk_manager.var_optimization(confidence_level=0.05, max_var=0.02)
        print(f"Status: {result['status']}")
        print("Optimal Weights:")
        for asset, weight in result['weights'].items():
            print(f"  {asset}: {weight:.1%}")
        print(f"Expected Return: {result['objective_value']:.1%}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n2. Conditional Value-at-Risk Optimization")
    print("-" * 40)
    try:
        result = risk_manager.cvar_optimization(confidence_level=0.05, max_cvar=0.03)
        print(f"Status: {result['status']}")
        print("Optimal Weights:")
        for asset, weight in result['weights'].items():
            print(f"  {asset}: {weight:.1%}")
        print(f"Expected Return: {result['objective_value']:.1%}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n3. Stress Testing")
    print("-" * 40)
    stress_scenarios = [
        {
            "name": "Market_Crash",
            "US_Stocks": -0.20,
            "International_Stocks": -0.25,
            "US_Bonds": 0.05,
            "Commodities": -0.15,
        },
        {
            "name": "Inflation_Shock",
            "US_Stocks": -0.10,
            "International_Stocks": -0.12,
            "US_Bonds": -0.08,
            "Commodities": 0.20,
        },
        {
            "name": "Interest_Rate_Shock",
            "US_Stocks": -0.05,
            "International_Stocks": -0.08,
            "US_Bonds": -0.15,
            "Commodities": -0.10,
        },
    ]
    
    try:
        results = risk_manager.stress_testing(stress_scenarios)
        for scenario_name, scenario_results in results.items():
            print(f"\n{scenario_name}:")
            print(f"  Portfolio Return: {scenario_results['portfolio_return']:.1%}")
            print(f"  Portfolio Volatility: {scenario_results['portfolio_volatility']:.1%}")
            print(f"  Sharpe Ratio: {scenario_results['sharpe_ratio']:.2f}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n4. Risk Budgeting")
    print("-" * 40)
    try:
        risk_budgets = [0.4, 0.3, 0.2, 0.1]  # Target risk contributions
        result = risk_manager.risk_budgeting(risk_budgets)
        print(f"Status: {result['status']}")
        print("Optimal Weights:")
        for asset, weight in result['weights'].items():
            print(f"  {asset}: {weight:.1%}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
