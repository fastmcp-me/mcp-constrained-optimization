#!/usr/bin/env python3
"""
N-Queens Problem using Constrained Optimization MCP Server

The N-Queens problem is a classic constraint satisfaction problem where we need to place
N queens on an N×N chessboard such that no two queens attack each other.

This example demonstrates:
- Constraint satisfaction problem solving
- OR-Tools constraint programming
- Visualization of the solution
"""

import numpy as np
import matplotlib.pyplot as plt
from constrained_opt_mcp.models.ortools_models import (
    ORToolsProblem,
    ORToolsVariable,
    ORToolsConstraint
)
from constrained_opt_mcp.solvers.ortools_solver import solve_problem

def solve_nqueens(n=8):
    """Solve the N-Queens problem using OR-Tools"""
    
    # Create problem
    problem = ORToolsProblem(
        name="N-Queens Problem",
        problem_type="constraint_programming"
    )
    
    # Create variables: queens[i] = column position of queen in row i
    queens = []
    for i in range(n):
        var = ORToolsVariable(
            name=f"queen_{i}",
            domain=list(range(n)),
            var_type="integer"
        )
        queens.append(var)
        problem.add_variable(var)
    
    # Add constraints
    for i in range(n):
        for j in range(i + 1, n):
            # No two queens in same column
            problem.add_constraint(ORToolsConstraint(
                name=f"different_columns_{i}_{j}",
                constraint_type="not_equal",
                variables=[queens[i], queens[j]]
            ))
            
            # No two queens on same diagonal
            # Diagonal constraint: |queens[i] - queens[j]| != |i - j|
            problem.add_constraint(ORToolsConstraint(
                name=f"different_diagonals_{i}_{j}",
                constraint_type="not_equal",
                variables=[queens[i], queens[j]],
                coefficients=[1, -1],
                constant=-(i - j)
            ))
            
            problem.add_constraint(ORToolsConstraint(
                name=f"different_anti_diagonals_{i}_{j}",
                constraint_type="not_equal",
                variables=[queens[i], queens[j]],
                coefficients=[1, 1],
                constant=-(i + j)
            ))
    
    # Solve the problem
    solution = solve_problem(problem)
    
    if solution.is_optimal:
        return [solution.variable_values[f"queen_{i}"] for i in range(n)]
    else:
        return None

def visualize_solution(queens, n):
    """Visualize the N-Queens solution on a chessboard"""
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    
    # Create chessboard
    board = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if (i + j) % 2 == 0:
                board[i, j] = 1
    
    ax.imshow(board, cmap='gray', alpha=0.3)
    
    # Place queens
    for i, j in enumerate(queens):
        ax.scatter(j, i, s=500, c='red', marker='o', edgecolors='black', linewidth=2)
        ax.text(j, i, 'Q', ha='center', va='center', fontsize=16, fontweight='bold', color='white')
    
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels([chr(65 + i) for i in range(n)])
    ax.set_yticklabels(range(1, n + 1))
    ax.set_title(f'{n}-Queens Problem Solution', fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def analyze_nqueens_performance():
    """Analyze performance for different board sizes"""
    sizes = [4, 6, 8, 10]
    solve_times = []
    solutions_found = []
    
    for n in sizes:
        print(f"Solving {n}-Queens problem...")
        import time
        start_time = time.time()
        
        solution = solve_nqueens(n)
        
        end_time = time.time()
        solve_time = end_time - start_time
        solve_times.append(solve_time)
        
        if solution:
            solutions_found.append(1)
            print(f"  Solution found in {solve_time:.3f} seconds")
        else:
            solutions_found.append(0)
            print(f"  No solution found in {solve_time:.3f} seconds")
    
    # Plot performance
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.plot(sizes, solve_times, 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('Board Size (N)')
    ax1.set_ylabel('Solve Time (seconds)')
    ax1.set_title('N-Queens Solve Time')
    ax1.grid(True, alpha=0.3)
    
    ax2.bar(sizes, solutions_found, color=['red' if x == 0 else 'green' for x in solutions_found])
    ax2.set_xlabel('Board Size (N)')
    ax2.set_ylabel('Solution Found')
    ax2.set_title('Solution Existence')
    ax2.set_ylim(0, 1.2)
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(['No', 'Yes'])
    
    plt.tight_layout()
    plt.show()
    
    return sizes, solve_times, solutions_found

if __name__ == "__main__":
    print("N-Queens Problem Solver")
    print("=" * 50)
    
    # Solve 8-Queens problem
    n = 8
    print(f"Solving {n}-Queens problem...")
    
    solution = solve_nqueens(n)
    
    if solution:
        print(f"Solution found: {solution}")
        print("Visualizing solution...")
        visualize_solution(solution, n)
    else:
        print("No solution found!")
    
    print("\nPerformance Analysis:")
    analyze_nqueens_performance()
