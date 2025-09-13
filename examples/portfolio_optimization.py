#!/usr/bin/env python3
"""
Advanced Portfolio Optimization using Constrained Optimization MCP Server

This example demonstrates various portfolio optimization strategies including:
- Markowitz mean-variance optimization
- Black-Litterman model
- Risk parity optimization
- ESG-constrained optimization
- Multi-period optimization

This example demonstrates:
- Convex optimization with CVXPY
- Complex financial constraints
- Risk management techniques
- Performance attribution
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from constrained_opt_mcp.models.cvxpy_models import (
    CVXPYProblem,
    CVXPYVariable,
    CVXPYConstraint
)
from constrained_opt_mcp.solvers.cvxpy_solver import solve_cvxpy_problem

def generate_financial_data(n_assets=20, n_periods=252):
    """Generate realistic financial data for portfolio optimization"""
    np.random.seed(42)
    
    # Generate asset names
    sectors = ['Technology', 'Healthcare', 'Financial', 'Consumer', 'Energy', 'Industrial']
    assets = []
    for i in range(n_assets):
        sector = sectors[i % len(sectors)]
        assets.append(f"{sector}_{i+1}")
    
    # Generate returns using factor model
    n_factors = 3
    factor_loadings = np.random.normal(0, 1, (n_assets, n_factors))
    factor_returns = np.random.normal(0, 0.02, (n_periods, n_factors))
    
    # Idiosyncratic returns
    idiosyncratic = np.random.normal(0, 0.01, (n_periods, n_assets))
    
    # Total returns
    returns = factor_returns @ factor_loadings.T + idiosyncratic
    
    # Calculate statistics
    expected_returns = np.mean(returns, axis=0)
    cov_matrix = np.cov(returns.T)
    
    # Add ESG scores
    esg_scores = np.random.uniform(60, 95, n_assets)
    
    # Add sector information
    sector_info = [sectors[i % len(sectors)] for i in range(n_assets)]
    
    return {
        'assets': assets,
        'returns': returns,
        'expected_returns': expected_returns,
        'cov_matrix': cov_matrix,
        'esg_scores': esg_scores,
        'sectors': sector_info
    }

def markowitz_optimization(data, risk_aversion=1.0, constraints=None):
    """Markowitz mean-variance optimization"""
    
    n_assets = len(data['assets'])
    expected_returns = data['expected_returns']
    cov_matrix = data['cov_matrix']
    
    # Create problem
    problem = CVXPYProblem(
        name="Markowitz Portfolio Optimization",
        problem_type="convex"
    )
    
    # Create variables
    weights = CVXPYVariable(
        name="weights",
        shape=(n_assets,),
        var_type="continuous"
    )
    problem.add_variable(weights)
    
    # Objective: maximize return - risk_aversion * risk
    portfolio_return = expected_returns @ weights
    portfolio_risk = cp.quad_form(weights, cov_matrix)
    
    problem.set_objective(
        objective_type="maximize",
        expression=portfolio_return - risk_aversion * portfolio_risk
    )
    
    # Basic constraints
    problem.add_constraint(CVXPYConstraint(
        name="weights_sum_to_one",
        constraint_type="equality",
        expression=cp.sum(weights),
        constant=1.0
    ))
    
    problem.add_constraint(CVXPYConstraint(
        name="no_short_selling",
        constraint_type="greater_equal",
        expression=weights,
        constant=0.0
    ))
    
    # Add custom constraints if provided
    if constraints:
        for constraint in constraints:
            problem.add_constraint(constraint)
    
    # Solve the problem
    solution = solve_cvxpy_problem(problem)
    
    if solution.is_optimal:
        optimal_weights = solution.variable_values['weights']
        portfolio_return_val = np.dot(expected_returns, optimal_weights)
        portfolio_risk_val = np.sqrt(np.dot(optimal_weights, np.dot(cov_matrix, optimal_weights)))
        
        return {
            'weights': optimal_weights,
            'expected_return': portfolio_return_val,
            'risk': portfolio_risk_val,
            'sharpe_ratio': portfolio_return_val / portfolio_risk_val
        }
    else:
        return None

def black_litterman_optimization(data, views, confidences, tau=0.05):
    """Black-Litterman model for portfolio optimization"""
    
    n_assets = len(data['assets'])
    expected_returns = data['expected_returns']
    cov_matrix = data['cov_matrix']
    
    # Market capitalization weights (equal weight as proxy)
    market_caps = np.ones(n_assets) / n_assets
    
    # Implied equilibrium returns
    pi = 2 * risk_aversion * np.dot(cov_matrix, market_caps)
    
    # Black-Litterman formula
    P = np.array(views)  # Pick matrix
    Q = np.array([0.05, 0.03])  # View returns
    Omega = np.diag(confidences)  # Uncertainty matrix
    
    # Black-Litterman expected returns
    M1 = np.linalg.inv(tau * cov_matrix)
    M2 = P.T @ np.linalg.inv(Omega) @ P
    M3 = M1 @ pi
    M4 = P.T @ np.linalg.inv(Omega) @ Q
    
    bl_expected_returns = np.linalg.inv(M1 + M2) @ (M3 + M4)
    
    # Update data with BL expected returns
    data_bl = data.copy()
    data_bl['expected_returns'] = bl_expected_returns
    
    return markowitz_optimization(data_bl, risk_aversion=1.0)

def risk_parity_optimization(data):
    """Risk parity portfolio optimization"""
    
    n_assets = len(data['assets'])
    cov_matrix = data['cov_matrix']
    
    # Create problem
    problem = CVXPYProblem(
        name="Risk Parity Portfolio",
        problem_type="convex"
    )
    
    # Create variables
    weights = CVXPYVariable(
        name="weights",
        shape=(n_assets,),
        var_type="continuous"
    )
    problem.add_variable(weights)
    
    # Risk contributions
    portfolio_variance = cp.quad_form(weights, cov_matrix)
    risk_contributions = []
    
    for i in range(n_assets):
        risk_contrib = weights[i] * (cov_matrix[i, :] @ weights) / portfolio_variance
        risk_contributions.append(risk_contrib)
    
    # Objective: minimize sum of squared deviations from equal risk contributions
    target_risk_contrib = 1.0 / n_assets
    objective = cp.sum([cp.square(rc - target_risk_contrib) for rc in risk_contributions])
    
    problem.set_objective(
        objective_type="minimize",
        expression=objective
    )
    
    # Constraints
    problem.add_constraint(CVXPYConstraint(
        name="weights_sum_to_one",
        constraint_type="equality",
        expression=cp.sum(weights),
        constant=1.0
    ))
    
    problem.add_constraint(CVXPYConstraint(
        name="no_short_selling",
        constraint_type="greater_equal",
        expression=weights,
        constant=0.0
    ))
    
    # Solve the problem
    solution = solve_cvxpy_problem(problem)
    
    if solution.is_optimal:
        optimal_weights = solution.variable_values['weights']
        portfolio_return = np.dot(data['expected_returns'], optimal_weights)
        portfolio_risk = np.sqrt(np.dot(optimal_weights, np.dot(cov_matrix, optimal_weights)))
        
        return {
            'weights': optimal_weights,
            'expected_return': portfolio_return,
            'risk': portfolio_risk,
            'sharpe_ratio': portfolio_return / portfolio_risk
        }
    else:
        return None

def esg_constrained_optimization(data, min_esg_score=80, sector_limits=None):
    """ESG-constrained portfolio optimization"""
    
    n_assets = len(data['assets'])
    expected_returns = data['expected_returns']
    cov_matrix = data['cov_matrix']
    esg_scores = data['esg_scores']
    sectors = data['sectors']
    
    # Create constraints
    constraints = []
    
    # ESG constraint
    constraints.append(CVXPYConstraint(
        name="esg_constraint",
        constraint_type="greater_equal",
        expression=esg_scores @ weights,
        constant=min_esg_score
    ))
    
    # Sector limits
    if sector_limits:
        for sector, max_weight in sector_limits.items():
            sector_indices = [i for i, s in enumerate(sectors) if s == sector]
            if sector_indices:
                sector_weights = [weights[i] for i in sector_indices]
                constraints.append(CVXPYConstraint(
                    name=f"sector_limit_{sector}",
                    constraint_type="less_equal",
                    expression=cp.sum(sector_weights),
                    constant=max_weight
                ))
    
    return markowitz_optimization(data, risk_aversion=1.0, constraints=constraints)

def efficient_frontier(data, risk_aversion_range=(0.1, 5.0), n_points=20):
    """Generate efficient frontier"""
    
    risk_aversions = np.linspace(risk_aversion_range[0], risk_aversion_range[1], n_points)
    returns = []
    risks = []
    
    for risk_aversion in risk_aversions:
        result = markowitz_optimization(data, risk_aversion=risk_aversion)
        if result:
            returns.append(result['expected_return'])
            risks.append(result['risk'])
    
    return np.array(returns), np.array(risks)

def visualize_portfolio_results(data, results, title="Portfolio Optimization Results"):
    """Visualize portfolio optimization results"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Portfolio weights
    weights = results['weights']
    assets = data['assets']
    
    # Sort by weight
    sorted_indices = np.argsort(weights)[::-1]
    top_assets = [assets[i] for i in sorted_indices[:10]]
    top_weights = [weights[i] for i in sorted_indices[:10]]
    
    ax1.bar(range(len(top_assets)), top_weights, color='skyblue', alpha=0.7)
    ax1.set_xlabel('Assets')
    ax1.set_ylabel('Weight')
    ax1.set_title('Top 10 Portfolio Weights')
    ax1.set_xticks(range(len(top_assets)))
    ax1.set_xticklabels(top_assets, rotation=45, ha='right')
    ax1.grid(True, alpha=0.3)
    
    # 2. Risk-return scatter
    individual_returns = data['expected_returns']
    individual_risks = np.sqrt(np.diag(data['cov_matrix']))
    
    ax2.scatter(individual_risks, individual_returns, alpha=0.6, s=50, label='Individual Assets')
    ax2.scatter(results['risk'], results['expected_return'], 
               color='red', s=200, marker='*', label='Optimal Portfolio')
    ax2.set_xlabel('Risk (Volatility)')
    ax2.set_ylabel('Expected Return')
    ax2.set_title('Risk-Return Profile')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Sector allocation
    sectors = data['sectors']
    sector_weights = {}
    for i, sector in enumerate(sectors):
        if sector not in sector_weights:
            sector_weights[sector] = 0
        sector_weights[sector] += weights[i]
    
    ax3.pie(sector_weights.values(), labels=sector_weights.keys(), autopct='%1.1f%%')
    ax3.set_title('Sector Allocation')
    
    # 4. Risk contribution
    cov_matrix = data['cov_matrix']
    portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
    risk_contributions = []
    
    for i in range(len(weights)):
        risk_contrib = weights[i] * (cov_matrix[i, :] @ weights) / portfolio_variance
        risk_contributions.append(risk_contrib)
    
    ax4.bar(range(len(assets)), risk_contributions, color='lightcoral', alpha=0.7)
    ax4.set_xlabel('Assets')
    ax4.set_ylabel('Risk Contribution')
    ax4.set_title('Risk Contribution by Asset')
    ax4.set_xticks(range(0, len(assets), 5))
    ax4.set_xticklabels([assets[i] for i in range(0, len(assets), 5)], rotation=45)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def compare_optimization_strategies(data):
    """Compare different portfolio optimization strategies"""
    
    print("Comparing Portfolio Optimization Strategies")
    print("=" * 50)
    
    # Markowitz optimization
    print("1. Markowitz Mean-Variance Optimization")
    markowitz_result = markowitz_optimization(data, risk_aversion=1.0)
    if markowitz_result:
        print(f"   Expected Return: {markowitz_result['expected_return']:.3f}")
        print(f"   Risk: {markowitz_result['risk']:.3f}")
        print(f"   Sharpe Ratio: {markowitz_result['sharpe_ratio']:.3f}")
    
    # Risk parity
    print("\n2. Risk Parity Optimization")
    risk_parity_result = risk_parity_optimization(data)
    if risk_parity_result:
        print(f"   Expected Return: {risk_parity_result['expected_return']:.3f}")
        print(f"   Risk: {risk_parity_result['risk']:.3f}")
        print(f"   Sharpe Ratio: {risk_parity_result['sharpe_ratio']:.3f}")
    
    # ESG-constrained
    print("\n3. ESG-Constrained Optimization")
    esg_result = esg_constrained_optimization(data, min_esg_score=80)
    if esg_result:
        print(f"   Expected Return: {esg_result['expected_return']:.3f}")
        print(f"   Risk: {esg_result['risk']:.3f}")
        print(f"   Sharpe Ratio: {esg_result['sharpe_ratio']:.3f}")
    
    # Efficient frontier
    print("\n4. Efficient Frontier Analysis")
    returns, risks = efficient_frontier(data)
    
    plt.figure(figsize=(10, 6))
    plt.plot(risks, returns, 'b-', linewidth=2, label='Efficient Frontier')
    plt.scatter(risks, returns, c='blue', alpha=0.6)
    
    if markowitz_result:
        plt.scatter(markowitz_result['risk'], markowitz_result['expected_return'], 
                   color='red', s=100, marker='*', label='Markowitz')
    
    if risk_parity_result:
        plt.scatter(risk_parity_result['risk'], risk_parity_result['expected_return'], 
                   color='green', s=100, marker='s', label='Risk Parity')
    
    if esg_result:
        plt.scatter(esg_result['risk'], esg_result['expected_return'], 
                   color='orange', s=100, marker='^', label='ESG-Constrained')
    
    plt.xlabel('Risk (Volatility)')
    plt.ylabel('Expected Return')
    plt.title('Portfolio Optimization Strategies Comparison')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

if __name__ == "__main__":
    print("Advanced Portfolio Optimization")
    print("=" * 50)
    
    # Generate sample data
    data = generate_financial_data(n_assets=20, n_periods=252)
    
    print(f"Generated data for {len(data['assets'])} assets")
    print(f"Expected returns range: {data['expected_returns'].min():.3f} to {data['expected_returns'].max():.3f}")
    print(f"Average volatility: {np.sqrt(np.diag(data['cov_matrix'])).mean():.3f}")
    
    # Run comparison
    compare_optimization_strategies(data)
    
    # Detailed analysis of Markowitz optimization
    print("\nDetailed Markowitz Analysis:")
    markowitz_result = markowitz_optimization(data, risk_aversion=1.0)
    if markowitz_result:
        visualize_portfolio_results(data, markowitz_result, "Markowitz Portfolio Optimization")
