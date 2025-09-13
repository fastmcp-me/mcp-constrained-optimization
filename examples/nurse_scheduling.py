#!/usr/bin/env python3
"""
Nurse Scheduling Problem using Constrained Optimization MCP Server

The nurse scheduling problem involves assigning nurses to shifts while satisfying
various constraints such as minimum coverage, maximum consecutive shifts, and
nurse preferences.

This example demonstrates:
- Constraint programming for scheduling
- OR-Tools for complex workforce scheduling
- Soft and hard constraints
- Fairness and preference considerations
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from constrained_opt_mcp.models.ortools_models import (
    ORToolsProblem,
    ORToolsVariable,
    ORToolsConstraint
)
from constrained_opt_mcp.solvers.ortools_solver import solve_problem

def solve_nurse_scheduling(nurses, shifts, days, requirements, preferences=None):
    """
    Solve nurse scheduling problem
    
    Args:
        nurses: List of nurse names
        shifts: List of shift names (e.g., ['Day', 'Evening', 'Night'])
        days: List of days (e.g., ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        requirements: Dict of (day, shift) -> required_nurses
        preferences: Dict of (nurse, day, shift) -> preference_score (optional)
    """
    
    n_nurses = len(nurses)
    n_shifts = len(shifts)
    n_days = len(days)
    
    # Create problem
    problem = ORToolsProblem(
        name="Nurse Scheduling",
        problem_type="constraint_programming"
    )
    
    # Create binary variables: x[nurse][day][shift] = 1 if nurse works that shift
    assignments = {}
    for i, nurse in enumerate(nurses):
        for j, day in enumerate(days):
            for k, shift in enumerate(shifts):
                var = ORToolsVariable(
                    name=f"assign_{nurse}_{day}_{shift}",
                    domain=[0, 1],
                    var_type="binary"
                )
                assignments[(nurse, day, shift)] = var
                problem.add_variable(var)
    
    # Objective: maximize preferences (if provided) or minimize total assignments
    if preferences:
        # Maximize total preference score
        objective_vars = []
        objective_coeffs = []
        
        for (nurse, day, shift), var in assignments.items():
            if (nurse, day, shift) in preferences:
                objective_vars.append(var)
                objective_coeffs.append(preferences[(nurse, day, shift)])
        
        if objective_vars:
            problem.set_objective(
                objective_type="maximize",
                coefficients=objective_coeffs,
                variables=objective_vars
            )
    else:
        # Minimize total assignments
        all_vars = list(assignments.values())
        problem.set_objective(
            objective_type="minimize",
            coefficients=[1] * len(all_vars),
            variables=all_vars
        )
    
    # Hard constraints
    
    # 1. Coverage requirements: each (day, shift) must have required number of nurses
    for day in days:
        for shift in shifts:
            if (day, shift) in requirements:
                required = requirements[(day, shift)]
                day_shift_vars = [assignments[(nurse, day, shift)] for nurse in nurses]
                
                problem.add_constraint(ORToolsConstraint(
                    name=f"coverage_{day}_{shift}",
                    constraint_type="greater_equal",
                    variables=day_shift_vars,
                    coefficients=[1] * n_nurses,
                    constant=required
                ))
    
    # 2. Each nurse can work at most one shift per day
    for nurse in nurses:
        for day in days:
            day_vars = [assignments[(nurse, day, shift)] for shift in shifts]
            problem.add_constraint(ORToolsConstraint(
                name=f"one_shift_per_day_{nurse}_{day}",
                constraint_type="less_equal",
                variables=day_vars,
                coefficients=[1] * n_shifts,
                constant=1
            ))
    
    # 3. No consecutive night shifts
    for nurse in nurses:
        for i in range(n_days - 1):
            night_today = assignments[(nurse, days[i], 'Night')]
            night_tomorrow = assignments[(nurse, days[i + 1], 'Night')]
            
            problem.add_constraint(ORToolsConstraint(
                name=f"no_consecutive_nights_{nurse}_{days[i]}",
                constraint_type="less_equal",
                variables=[night_today, night_tomorrow],
                coefficients=[1, 1],
                constant=1
            ))
    
    # 4. Maximum 5 shifts per week
    for nurse in nurses:
        week_vars = [assignments[(nurse, day, shift)] for day in days for shift in shifts]
        problem.add_constraint(ORToolsConstraint(
            name=f"max_shifts_per_week_{nurse}",
            constraint_type="less_equal",
            variables=week_vars,
            coefficients=[1] * len(week_vars),
            constant=5
        ))
    
    # 5. At least 2 days off per week
    for nurse in nurses:
        # Count days with no shifts
        no_shift_vars = []
        for day in days:
            day_vars = [assignments[(nurse, day, shift)] for shift in shifts]
            # Create auxiliary variable for "no shift on this day"
            no_shift_var = ORToolsVariable(
                name=f"no_shift_{nurse}_{day}",
                domain=[0, 1],
                var_type="binary"
            )
            problem.add_variable(no_shift_var)
            no_shift_vars.append(no_shift_var)
            
            # no_shift_var = 1 if sum of day_vars = 0
            problem.add_constraint(ORToolsConstraint(
                name=f"no_shift_logic_{nurse}_{day}",
                constraint_type="equality",
                variables=no_shift_vars[-1:] + day_vars,
                coefficients=[1] + [-1] * n_shifts,
                constant=0
            ))
        
        problem.add_constraint(ORToolsConstraint(
            name=f"min_days_off_{nurse}",
            constraint_type="greater_equal",
            variables=no_shift_vars,
            coefficients=[1] * n_days,
            constant=2
        ))
    
    # Solve the problem
    solution = solve_problem(problem)
    
    if solution.is_optimal:
        result = {
            'assignments': {},
            'summary': {
                'total_assignments': 0,
                'nurse_workload': {},
                'shift_coverage': {}
            }
        }
        
        # Extract assignments
        for (nurse, day, shift), var in assignments.items():
            if solution.variable_values[f"assign_{nurse}_{day}_{shift}"] == 1:
                if nurse not in result['assignments']:
                    result['assignments'][nurse] = {}
                if day not in result['assignments'][nurse]:
                    result['assignments'][nurse][day] = []
                result['assignments'][nurse][day].append(shift)
                result['summary']['total_assignments'] += 1
        
        # Calculate nurse workloads
        for nurse in nurses:
            workload = 0
            if nurse in result['assignments']:
                for day_assignments in result['assignments'][nurse].values():
                    workload += len(day_assignments)
            result['summary']['nurse_workload'][nurse] = workload
        
        # Calculate shift coverage
        for day in days:
            for shift in shifts:
                coverage = 0
                for nurse in nurses:
                    if (nurse in result['assignments'] and 
                        day in result['assignments'][nurse] and 
                        shift in result['assignments'][nurse][day]):
                        coverage += 1
                result['summary']['shift_coverage'][(day, shift)] = coverage
        
        return result
    else:
        return None

def visualize_nurse_schedule(assignments, nurses, shifts, days):
    """Visualize nurse schedule as a heatmap"""
    
    # Create schedule matrix
    schedule_matrix = np.zeros((len(nurses), len(days) * len(shifts)))
    
    for i, nurse in enumerate(nurses):
        for j, day in enumerate(days):
            for k, shift in enumerate(shifts):
                col_idx = j * len(shifts) + k
                if (nurse in assignments and 
                    day in assignments[nurse] and 
                    shift in assignments[nurse][day]):
                    schedule_matrix[i, col_idx] = 1
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Create labels for x-axis
    x_labels = []
    for day in days:
        for shift in shifts:
            x_labels.append(f"{day}\n{shift}")
    
    im = ax.imshow(schedule_matrix, cmap='RdYlGn', aspect='auto')
    
    # Set ticks and labels
    ax.set_xticks(range(len(x_labels)))
    ax.set_xticklabels(x_labels, rotation=45, ha='right')
    ax.set_yticks(range(len(nurses)))
    ax.set_yticklabels(nurses)
    
    # Add grid
    ax.set_xticks(np.arange(-0.5, len(x_labels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(nurses), 1), minor=True)
    ax.grid(which="minor", color="black", linestyle='-', linewidth=0.5)
    
    ax.set_title('Nurse Schedule', fontsize=16, fontweight='bold')
    ax.set_xlabel('Day and Shift')
    ax.set_ylabel('Nurse')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Assignment (1=Assigned, 0=Not Assigned)')
    
    plt.tight_layout()
    plt.show()

def analyze_schedule_quality(result, requirements):
    """Analyze the quality of the generated schedule"""
    
    print("Schedule Quality Analysis")
    print("=" * 40)
    
    # Coverage analysis
    print("\n1. Coverage Analysis:")
    for (day, shift), required in requirements.items():
        actual = result['summary']['shift_coverage'].get((day, shift), 0)
        status = "✓" if actual >= required else "✗"
        print(f"   {day} {shift}: {actual}/{required} {status}")
    
    # Workload analysis
    print("\n2. Workload Distribution:")
    workloads = list(result['summary']['nurse_workload'].values())
    print(f"   Average workload: {np.mean(workloads):.1f}")
    print(f"   Workload range: {min(workloads)}-{max(workloads)}")
    print(f"   Workload std: {np.std(workloads):.1f}")
    
    # Fairness analysis
    print("\n3. Fairness Analysis:")
    if len(workloads) > 1:
        fairness_score = 1 - (np.std(workloads) / np.mean(workloads))
        print(f"   Fairness score: {fairness_score:.3f} (1.0 = perfectly fair)")
    
    # Weekend analysis
    print("\n4. Weekend Coverage:")
    weekend_days = ['Sat', 'Sun']
    weekend_coverage = 0
    for day in weekend_days:
        for shift in ['Day', 'Evening', 'Night']:
            if (day, shift) in result['summary']['shift_coverage']:
                weekend_coverage += result['summary']['shift_coverage'][(day, shift)]
    print(f"   Total weekend assignments: {weekend_coverage}")

def generate_nurse_scheduling_data(n_nurses=8, n_days=7):
    """Generate sample nurse scheduling data"""
    
    nurses = [f"Nurse_{i+1}" for i in range(n_nurses)]
    shifts = ['Day', 'Evening', 'Night']
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Coverage requirements
    requirements = {}
    for day in days:
        for shift in shifts:
            if day in ['Sat', 'Sun']:
                # Weekend: higher requirements
                requirements[(day, shift)] = 2
            else:
                # Weekday: normal requirements
                requirements[(day, shift)] = 1
    
    # Nurse preferences (optional)
    preferences = {}
    np.random.seed(42)
    
    for nurse in nurses:
        for day in days:
            for shift in shifts:
                # Random preferences (0-10 scale)
                preference = np.random.randint(0, 11)
                preferences[(nurse, day, shift)] = preference
    
    return nurses, shifts, days, requirements, preferences

if __name__ == "__main__":
    print("Nurse Scheduling Problem Solver")
    print("=" * 50)
    
    # Generate sample data
    nurses, shifts, days, requirements, preferences = generate_nurse_scheduling_data()
    
    print(f"Nurses: {nurses}")
    print(f"Shifts: {shifts}")
    print(f"Days: {days}")
    print(f"Requirements: {requirements}")
    
    # Solve the problem
    print("\nSolving nurse scheduling problem...")
    result = solve_nurse_scheduling(nurses, shifts, days, requirements, preferences)
    
    if result:
        print("Solution found!")
        print(f"Total assignments: {result['summary']['total_assignments']}")
        
        # Print schedule
        print("\nGenerated Schedule:")
        for nurse in nurses:
            if nurse in result['assignments']:
                print(f"\n{nurse}:")
                for day, shift_list in result['assignments'][nurse].items():
                    print(f"  {day}: {', '.join(shift_list)}")
            else:
                print(f"\n{nurse}: No assignments")
        
        # Visualize schedule
        print("\nVisualizing schedule...")
        visualize_nurse_schedule(result['assignments'], nurses, shifts, days)
        
        # Analyze quality
        analyze_schedule_quality(result, requirements)
        
    else:
        print("No solution found!")
