#!/usr/bin/env python3
"""
Economic Production Planning using Constrained Optimization MCP Server

This example demonstrates production planning with economic considerations including:
- Multi-period production planning
- Inventory management
- Capacity constraints
- Demand forecasting
- Cost minimization
- Resource allocation

This example demonstrates:
- Linear programming with HiGHS
- Multi-period optimization
- Economic modeling
- Supply chain optimization
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from constrained_opt_mcp.models.highs_models import (
    HiGHSProblem,
    HiGHSVariable,
    HiGHSConstraint
)
from constrained_opt_mcp.solvers.highs_solver import solve_problem

def solve_production_planning(products, periods, demand, costs, capacities, initial_inventory=None):
    """
    Solve multi-period production planning problem
    
    Args:
        products: List of product names
        periods: List of period names
        demand: Dict of (product, period) -> demand_quantity
        costs: Dict with cost information
        capacities: Dict with capacity constraints
        initial_inventory: Dict of product -> initial_inventory
    """
    
    n_products = len(products)
    n_periods = len(periods)
    
    # Create problem
    problem = HiGHSProblem(
        name="Production Planning",
        problem_type="linear_programming"
    )
    
    # Create variables
    variables = {}
    
    # Production variables: x[product][period] = production quantity
    for product in products:
        for period in periods:
            var = HiGHSVariable(
                name=f"prod_{product}_{period}",
                lower_bound=0,
                upper_bound=capacities.get('production', {}).get(product, float('inf')),
                var_type="continuous"
            )
            variables[f"prod_{product}_{period}"] = var
            problem.add_variable(var)
    
    # Inventory variables: I[product][period] = inventory level
    for product in products:
        for period in periods:
            var = HiGHSVariable(
                name=f"inv_{product}_{period}",
                lower_bound=0,
                upper_bound=capacities.get('inventory', {}).get(product, float('inf')),
                var_type="continuous"
            )
            variables[f"inv_{product}_{period}"] = var
            problem.add_variable(var)
    
    # Shortage variables: s[product][period] = shortage quantity
    for product in products:
        for period in periods:
            var = HiGHSVariable(
                name=f"short_{product}_{period}",
                lower_bound=0,
                var_type="continuous"
            )
            variables[f"short_{product}_{period}"] = var
            problem.add_variable(var)
    
    # Objective: minimize total cost
    objective_vars = []
    objective_coeffs = []
    
    # Production costs
    for product in products:
        for period in periods:
            objective_vars.append(variables[f"prod_{product}_{period}"])
            objective_coeffs.append(costs['production'].get(product, 0))
    
    # Inventory holding costs
    for product in products:
        for period in periods:
            objective_vars.append(variables[f"inv_{product}_{period}"])
            objective_coeffs.append(costs['holding'].get(product, 0))
    
    # Shortage costs
    for product in products:
        for period in periods:
            objective_vars.append(variables[f"short_{product}_{period}"])
            objective_coeffs.append(costs['shortage'].get(product, 0))
    
    problem.set_objective(
        objective_type="minimize",
        coefficients=objective_coeffs,
        variables=objective_vars
    )
    
    # Constraints
    
    # 1. Inventory balance constraints
    for product in products:
        for i, period in enumerate(periods):
            # I[product][period] = I[product][period-1] + x[product][period] - demand[product][period] + s[product][period]
            
            if i == 0:
                # First period
                initial_inv = initial_inventory.get(product, 0) if initial_inventory else 0
                problem.add_constraint(HiGHSConstraint(
                    name=f"inventory_balance_{product}_{period}",
                    constraint_type="equality",
                    variables=[
                        variables[f"inv_{product}_{period}"],
                        variables[f"prod_{product}_{period}"],
                        variables[f"short_{product}_{period}"]
                    ],
                    coefficients=[1, 1, 1],
                    constant=initial_inv - demand.get((product, period), 0)
                ))
            else:
                # Subsequent periods
                prev_period = periods[i-1]
                problem.add_constraint(HiGHSConstraint(
                    name=f"inventory_balance_{product}_{period}",
                    constraint_type="equality",
                    variables=[
                        variables[f"inv_{product}_{period}"],
                        variables[f"inv_{product}_{prev_period}"],
                        variables[f"prod_{product}_{period}"],
                        variables[f"short_{product}_{period}"]
                    ],
                    coefficients=[1, -1, 1, 1],
                    constant=-demand.get((product, period), 0)
                ))
    
    # 2. Production capacity constraints
    for period in periods:
        total_capacity = capacities.get('total_production', {}).get(period, float('inf'))
        if total_capacity < float('inf'):
            period_vars = [variables[f"prod_{product}_{period}"] for product in products]
            problem.add_constraint(HiGHSConstraint(
                name=f"total_capacity_{period}",
                constraint_type="less_equal",
                variables=period_vars,
                coefficients=[1] * n_products,
                constant=total_capacity
            ))
    
    # 3. Resource constraints (if specified)
    if 'resources' in capacities:
        for resource, resource_capacity in capacities['resources'].items():
            for period in periods:
                if resource_capacity.get(period, float('inf')) < float('inf'):
                    resource_vars = []
                    resource_coeffs = []
                    
                    for product in products:
                        if (product, resource) in costs.get('resource_usage', {}):
                            resource_vars.append(variables[f"prod_{product}_{period}"])
                            resource_coeffs.append(costs['resource_usage'][(product, resource)])
                    
                    if resource_vars:
                        problem.add_constraint(HiGHSConstraint(
                            name=f"resource_{resource}_{period}",
                            constraint_type="less_equal",
                            variables=resource_vars,
                            coefficients=resource_coeffs,
                            constant=resource_capacity[period]
                        ))
    
    # Solve the problem
    solution = solve_problem(problem)
    
    if solution.is_optimal:
        result = {
            'production': {},
            'inventory': {},
            'shortage': {},
            'total_cost': solution.objective_value,
            'summary': {
                'total_production': 0,
                'total_inventory': 0,
                'total_shortage': 0
            }
        }
        
        # Extract solution
        for product in products:
            result['production'][product] = {}
            result['inventory'][product] = {}
            result['shortage'][product] = {}
            
            for period in periods:
                prod_val = solution.variable_values[f"prod_{product}_{period}"]
                inv_val = solution.variable_values[f"inv_{product}_{period}"]
                short_val = solution.variable_values[f"short_{product}_{period}"]
                
                result['production'][product][period] = prod_val
                result['inventory'][product][period] = inv_val
                result['shortage'][product][period] = short_val
                
                result['summary']['total_production'] += prod_val
                result['summary']['total_inventory'] += inv_val
                result['summary']['total_shortage'] += short_val
        
        return result
    else:
        return None

def visualize_production_plan(result, products, periods):
    """Visualize production planning results"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Production quantities over time
    for product in products:
        production_values = [result['production'][product][period] for period in periods]
        ax1.plot(periods, production_values, marker='o', label=product, linewidth=2)
    
    ax1.set_xlabel('Period')
    ax1.set_ylabel('Production Quantity')
    ax1.set_title('Production Schedule')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Inventory levels over time
    for product in products:
        inventory_values = [result['inventory'][product][period] for period in periods]
        ax2.plot(periods, inventory_values, marker='s', label=product, linewidth=2)
    
    ax2.set_xlabel('Period')
    ax2.set_ylabel('Inventory Level')
    ax2.set_title('Inventory Levels')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Shortage levels over time
    for product in products:
        shortage_values = [result['shortage'][product][period] for period in periods]
        ax3.plot(periods, shortage_values, marker='^', label=product, linewidth=2)
    
    ax3.set_xlabel('Period')
    ax3.set_ylabel('Shortage Quantity')
    ax3.set_title('Shortage Levels')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Total production by product
    total_production = [sum(result['production'][product].values()) for product in products]
    ax4.bar(products, total_production, color='skyblue', alpha=0.7)
    ax4.set_xlabel('Product')
    ax4.set_ylabel('Total Production')
    ax4.set_title('Total Production by Product')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def generate_production_data(n_products=3, n_periods=12):
    """Generate sample production planning data"""
    
    np.random.seed(42)
    
    products = [f"Product_{i+1}" for i in range(n_products)]
    periods = [f"Period_{i+1}" for i in range(n_periods)]
    
    # Demand (with seasonality)
    demand = {}
    for product in products:
        base_demand = np.random.randint(50, 150)
        for i, period in enumerate(periods):
            # Add seasonality
            seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * i / 12)
            demand[(product, period)] = int(base_demand * seasonal_factor)
    
    # Costs
    costs = {
        'production': {product: np.random.uniform(10, 50) for product in products},
        'holding': {product: np.random.uniform(1, 5) for product in products},
        'shortage': {product: np.random.uniform(20, 100) for product in products},
        'resource_usage': {
            (product, 'labor'): np.random.uniform(0.5, 2.0) for product in products
        }
    }
    
    # Capacities
    capacities = {
        'production': {product: np.random.randint(100, 300) for product in products},
        'inventory': {product: np.random.randint(200, 500) for product in products},
        'total_production': {period: np.random.randint(400, 800) for period in periods},
        'resources': {
            'labor': {period: np.random.randint(200, 400) for period in periods}
        }
    }
    
    # Initial inventory
    initial_inventory = {product: np.random.randint(50, 150) for product in products}
    
    return products, periods, demand, costs, capacities, initial_inventory

def analyze_production_efficiency(result, demand, costs):
    """Analyze production efficiency and performance metrics"""
    
    print("Production Efficiency Analysis")
    print("=" * 40)
    
    # Service level analysis
    print("\n1. Service Level Analysis:")
    total_demand = sum(demand.values())
    total_shortage = result['summary']['total_shortage']
    service_level = (total_demand - total_shortage) / total_demand
    print(f"   Service Level: {service_level:.1%}")
    print(f"   Total Demand: {total_demand:.0f}")
    print(f"   Total Shortage: {total_shortage:.0f}")
    
    # Cost analysis
    print("\n2. Cost Analysis:")
    print(f"   Total Cost: ${result['total_cost']:.2f}")
    
    # Production efficiency
    print("\n3. Production Efficiency:")
    total_production = result['summary']['total_production']
    total_inventory = result['summary']['total_inventory']
    inventory_turnover = total_production / (total_inventory + 1e-6)
    print(f"   Inventory Turnover: {inventory_turnover:.2f}")
    print(f"   Total Production: {total_production:.0f}")
    print(f"   Average Inventory: {total_inventory / len(result['inventory']):.0f}")
    
    # Resource utilization
    print("\n4. Resource Utilization:")
    for product in result['production']:
        avg_production = np.mean(list(result['production'][product].values()))
        print(f"   {product}: {avg_production:.1f} units/period")

def compare_production_strategies(products, periods, demand, costs, capacities, initial_inventory):
    """Compare different production planning strategies"""
    
    print("Comparing Production Planning Strategies")
    print("=" * 50)
    
    # Strategy 1: Just-in-time (minimize inventory)
    print("1. Just-in-Time Strategy")
    jit_costs = costs.copy()
    jit_costs['holding'] = {product: cost * 10 for product, cost in costs['holding'].items()}
    
    jit_result = solve_production_planning(products, periods, demand, jit_costs, capacities, initial_inventory)
    if jit_result:
        print(f"   Total Cost: ${jit_result['total_cost']:.2f}")
        print(f"   Service Level: {(sum(demand.values()) - jit_result['summary']['total_shortage']) / sum(demand.values()):.1%}")
    
    # Strategy 2: Safety stock (minimize shortage)
    print("\n2. Safety Stock Strategy")
    ss_costs = costs.copy()
    ss_costs['shortage'] = {product: cost * 10 for product, cost in costs['shortage'].items()}
    
    ss_result = solve_production_planning(products, periods, demand, ss_costs, capacities, initial_inventory)
    if ss_result:
        print(f"   Total Cost: ${ss_result['total_cost']:.2f}")
        print(f"   Service Level: {(sum(demand.values()) - ss_result['summary']['total_shortage']) / sum(demand.values()):.1%}")
    
    # Strategy 3: Balanced approach
    print("\n3. Balanced Strategy")
    balanced_result = solve_production_planning(products, periods, demand, costs, capacities, initial_inventory)
    if balanced_result:
        print(f"   Total Cost: ${balanced_result['total_cost']:.2f}")
        print(f"   Service Level: {(sum(demand.values()) - balanced_result['summary']['total_shortage']) / sum(demand.values()):.1%}")
    
    # Compare strategies
    strategies = [
        ("Just-in-Time", jit_result),
        ("Safety Stock", ss_result),
        ("Balanced", balanced_result)
    ]
    
    costs_comparison = []
    service_levels = []
    
    for name, result in strategies:
        if result:
            costs_comparison.append(result['total_cost'])
            service_level = (sum(demand.values()) - result['summary']['total_shortage']) / sum(demand.values())
            service_levels.append(service_level)
        else:
            costs_comparison.append(float('inf'))
            service_levels.append(0)
    
    # Plot comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    strategy_names = [name for name, _ in strategies]
    
    ax1.bar(strategy_names, costs_comparison, color=['red', 'blue', 'green'], alpha=0.7)
    ax1.set_ylabel('Total Cost ($)')
    ax1.set_title('Cost Comparison')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    ax2.bar(strategy_names, service_levels, color=['red', 'blue', 'green'], alpha=0.7)
    ax2.set_ylabel('Service Level')
    ax2.set_title('Service Level Comparison')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("Economic Production Planning")
    print("=" * 50)
    
    # Generate sample data
    products, periods, demand, costs, capacities, initial_inventory = generate_production_data()
    
    print(f"Products: {products}")
    print(f"Periods: {periods}")
    print(f"Total demand: {sum(demand.values())}")
    print(f"Initial inventory: {initial_inventory}")
    
    # Solve production planning
    print("\nSolving production planning problem...")
    result = solve_production_planning(products, periods, demand, costs, capacities, initial_inventory)
    
    if result:
        print("Solution found!")
        print(f"Total cost: ${result['total_cost']:.2f}")
        
        # Visualize results
        print("\nVisualizing production plan...")
        visualize_production_plan(result, products, periods)
        
        # Analyze efficiency
        analyze_production_efficiency(result, demand, costs)
        
        # Compare strategies
        print("\nComparing production strategies...")
        compare_production_strategies(products, periods, demand, costs, capacities, initial_inventory)
        
    else:
        print("No solution found!")
