#!/usr/bin/env python3
"""
Knapsack Problem using Constrained Optimization MCP Server

The knapsack problem is a classic optimization problem where we have a set of items,
each with a weight and value, and we want to maximize the total value while staying
within a weight limit.

This example demonstrates:
- Integer programming
- OR-Tools constraint programming
- Binary decision variables
- Multiple knapsack variants
"""

import numpy as np
import matplotlib.pyplot as plt
from constrained_opt_mcp.models.ortools_models import (
    ORToolsProblem,
    ORToolsVariable,
    ORToolsConstraint
)
from constrained_opt_mcp.solvers.ortools_solver import solve_problem

def solve_knapsack(values, weights, capacity):
    """Solve the 0/1 knapsack problem"""
    
    n_items = len(values)
    
    # Create problem
    problem = ORToolsProblem(
        name="Knapsack Problem",
        problem_type="constraint_programming"
    )
    
    # Create binary variables: x[i] = 1 if item i is selected
    items = []
    for i in range(n_items):
        var = ORToolsVariable(
            name=f"item_{i}",
            domain=[0, 1],
            var_type="binary"
        )
        items.append(var)
        problem.add_variable(var)
    
    # Objective: maximize total value
    problem.set_objective(
        objective_type="maximize",
        coefficients=values,
        variables=items
    )
    
    # Constraint: total weight <= capacity
    problem.add_constraint(ORToolsConstraint(
        name="weight_constraint",
        constraint_type="less_equal",
        variables=items,
        coefficients=weights,
        constant=capacity
    ))
    
    # Solve the problem
    solution = solve_problem(problem)
    
    if solution.is_optimal:
        selected_items = [solution.variable_values[f"item_{i}"] for i in range(n_items)]
        total_value = sum(values[i] * selected_items[i] for i in range(n_items))
        total_weight = sum(weights[i] * selected_items[i] for i in range(n_items))
        
        return {
            'selected_items': selected_items,
            'total_value': total_value,
            'total_weight': total_weight,
            'capacity': capacity
        }
    else:
        return None

def solve_multiple_knapsack(values, weights, capacities):
    """Solve the multiple knapsack problem"""
    
    n_items = len(values)
    n_knapsacks = len(capacities)
    
    # Create problem
    problem = ORToolsProblem(
        name="Multiple Knapsack Problem",
        problem_type="constraint_programming"
    )
    
    # Create binary variables: x[i][j] = 1 if item i is in knapsack j
    items = []
    for i in range(n_items):
        for j in range(n_knapsacks):
            var = ORToolsVariable(
                name=f"item_{i}_knapsack_{j}",
                domain=[0, 1],
                var_type="binary"
            )
            items.append(var)
            problem.add_variable(var)
    
    # Objective: maximize total value
    objective_coeffs = []
    for i in range(n_items):
        for j in range(n_knapsacks):
            objective_coeffs.append(values[i])
    
    problem.set_objective(
        objective_type="maximize",
        coefficients=objective_coeffs,
        variables=items
    )
    
    # Constraints: each item can be in at most one knapsack
    for i in range(n_items):
        item_vars = [items[i * n_knapsacks + j] for j in range(n_knapsacks)]
        problem.add_constraint(ORToolsConstraint(
            name=f"item_{i}_unique",
            constraint_type="less_equal",
            variables=item_vars,
            coefficients=[1] * n_knapsacks,
            constant=1
        ))
    
    # Constraints: each knapsack weight limit
    for j in range(n_knapsacks):
        knapsack_vars = [items[i * n_knapsacks + j] for i in range(n_items)]
        knapsack_weights = [weights[i] for i in range(n_items)]
        
        problem.add_constraint(ORToolsConstraint(
            name=f"knapsack_{j}_capacity",
            constraint_type="less_equal",
            variables=knapsack_vars,
            coefficients=knapsack_weights,
            constant=capacities[j]
        ))
    
    # Solve the problem
    solution = solve_problem(problem)
    
    if solution.is_optimal:
        result = {
            'assignments': {},
            'total_value': 0,
            'knapsack_weights': [0] * n_knapsacks
        }
        
        for i in range(n_items):
            for j in range(n_knapsacks):
                var_name = f"item_{i}_knapsack_{j}"
                if solution.variable_values[var_name] == 1:
                    if j not in result['assignments']:
                        result['assignments'][j] = []
                    result['assignments'][j].append(i)
                    result['total_value'] += values[i]
                    result['knapsack_weights'][j] += weights[i]
        
        return result
    else:
        return None

def visualize_knapsack_solution(values, weights, solution, capacity):
    """Visualize the knapsack solution"""
    if not solution:
        print("No solution found!")
        return
    
    selected_items = solution['selected_items']
    total_value = solution['total_value']
    total_weight = solution['total_weight']
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: Item selection
    n_items = len(values)
    x_pos = np.arange(n_items)
    
    colors = ['green' if selected_items[i] else 'red' for i in range(n_items)]
    bars = ax1.bar(x_pos, values, color=colors, alpha=0.7)
    
    ax1.set_xlabel('Item Index')
    ax1.set_ylabel('Value')
    ax1.set_title('Knapsack Solution: Selected Items')
    ax1.set_xticks(x_pos)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, values)):
        if selected_items[i]:
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{value}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: Weight vs Value scatter
    selected_values = [values[i] for i in range(n_items) if selected_items[i]]
    selected_weights = [weights[i] for i in range(n_items) if selected_items[i]]
    unselected_values = [values[i] for i in range(n_items) if not selected_items[i]]
    unselected_weights = [weights[i] for i in range(n_items) if not selected_items[i]]
    
    ax2.scatter(selected_weights, selected_values, c='green', s=100, alpha=0.7, label='Selected')
    ax2.scatter(unselected_weights, unselected_values, c='red', s=100, alpha=0.7, label='Not Selected')
    
    ax2.set_xlabel('Weight')
    ax2.set_ylabel('Value')
    ax2.set_title('Weight vs Value Distribution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Add capacity line
    ax2.axvline(x=capacity, color='blue', linestyle='--', alpha=0.7, label=f'Capacity: {capacity}')
    ax2.legend()
    
    plt.tight_layout()
    plt.show()
    
    # Print summary
    print(f"\nKnapsack Solution Summary:")
    print(f"Total Value: {total_value}")
    print(f"Total Weight: {total_weight}/{capacity}")
    print(f"Capacity Utilization: {total_weight/capacity:.1%}")
    print(f"Selected Items: {[i for i in range(n_items) if selected_items[i]]}")

def generate_knapsack_data(n_items=20, max_value=100, max_weight=50):
    """Generate random knapsack data"""
    np.random.seed(42)
    
    values = np.random.randint(1, max_value + 1, n_items)
    weights = np.random.randint(1, max_weight + 1, n_items)
    capacity = int(0.6 * sum(weights))  # 60% of total weight
    
    return values, weights, capacity

def analyze_knapsack_performance():
    """Analyze performance for different problem sizes"""
    sizes = [10, 20, 50, 100]
    solve_times = []
    optimal_values = []
    
    for n in sizes:
        print(f"Solving knapsack with {n} items...")
        
        values, weights, capacity = generate_knapsack_data(n)
        
        import time
        start_time = time.time()
        solution = solve_knapsack(values, weights, capacity)
        end_time = time.time()
        
        solve_time = end_time - start_time
        solve_times.append(solve_time)
        
        if solution:
            optimal_values.append(solution['total_value'])
            print(f"  Optimal value: {solution['total_value']}, Time: {solve_time:.3f}s")
        else:
            optimal_values.append(0)
            print(f"  No solution found, Time: {solve_time:.3f}s")
    
    # Plot performance
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.plot(sizes, solve_times, 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('Number of Items')
    ax1.set_ylabel('Solve Time (seconds)')
    ax1.set_title('Knapsack Solve Time')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(sizes, optimal_values, 'go-', linewidth=2, markersize=8)
    ax2.set_xlabel('Number of Items')
    ax2.set_ylabel('Optimal Value')
    ax2.set_title('Optimal Values')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("Knapsack Problem Solver")
    print("=" * 50)
    
    # Generate sample data
    values, weights, capacity = generate_knapsack_data(20)
    
    print(f"Problem: {len(values)} items, capacity = {capacity}")
    print(f"Values: {values}")
    print(f"Weights: {weights}")
    
    # Solve single knapsack
    print("\nSolving single knapsack problem...")
    solution = solve_knapsack(values, weights, capacity)
    
    if solution:
        visualize_knapsack_solution(values, weights, solution, capacity)
    else:
        print("No solution found!")
    
    # Solve multiple knapsack
    print("\nSolving multiple knapsack problem...")
    capacities = [capacity // 2, capacity // 2]
    multi_solution = solve_multiple_knapsack(values, weights, capacities)
    
    if multi_solution:
        print(f"Multiple knapsack solution:")
        print(f"Total value: {multi_solution['total_value']}")
        for knapsack, items in multi_solution['assignments'].items():
            print(f"Knapsack {knapsack}: items {items}, weight: {multi_solution['knapsack_weights'][knapsack]}")
    
    print("\nPerformance Analysis:")
    analyze_knapsack_performance()
