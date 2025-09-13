#!/usr/bin/env python3
"""
Job Shop Scheduling Problem using Constrained Optimization MCP Server

The job shop scheduling problem involves scheduling a set of jobs on a set of machines
where each job consists of a sequence of operations, and each operation must be performed
on a specific machine for a specific duration.

This example demonstrates:
- Constraint programming for scheduling
- OR-Tools for complex scheduling problems
- Resource allocation and timing constraints
- Makespan minimization
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

def solve_job_shop_scheduling(jobs, machines, processing_times):
    """
    Solve job shop scheduling problem
    
    Args:
        jobs: List of job names
        machines: List of machine names
        processing_times: Dict of (job, machine) -> processing_time
    """
    
    n_jobs = len(jobs)
    n_machines = len(machines)
    
    # Create problem
    problem = ORToolsProblem(
        name="Job Shop Scheduling",
        problem_type="constraint_programming"
    )
    
    # Create variables for start times of each operation
    start_times = {}
    for job in jobs:
        for machine in machines:
            if (job, machine) in processing_times:
                var = ORToolsVariable(
                    name=f"start_{job}_{machine}",
                    domain=list(range(1000)),  # Large enough domain
                    var_type="integer"
                )
                start_times[(job, machine)] = var
                problem.add_variable(var)
    
    # Create makespan variable
    makespan_var = ORToolsVariable(
        name="makespan",
        domain=list(range(1000)),
        var_type="integer"
    )
    problem.add_variable(makespan_var)
    
    # Objective: minimize makespan
    problem.set_objective(
        objective_type="minimize",
        coefficients=[1],
        variables=[makespan_var]
    )
    
    # Constraints: makespan >= completion time of each operation
    for (job, machine), start_var in start_times.items():
        processing_time = processing_times[(job, machine)]
        problem.add_constraint(ORToolsConstraint(
            name=f"makespan_{job}_{machine}",
            constraint_type="greater_equal",
            variables=[makespan_var, start_var],
            coefficients=[1, -1],
            constant=processing_time
        ))
    
    # Constraints: no two operations on same machine at same time
    for machine in machines:
        machine_operations = [(job, machine) for job in jobs if (job, machine) in processing_times]
        
        for i, (job1, _) in enumerate(machine_operations):
            for j, (job2, _) in enumerate(machine_operations):
                if i != j:
                    start1 = start_times[(job1, machine)]
                    start2 = start_times[(job2, machine)]
                    time1 = processing_times[(job1, machine)]
                    time2 = processing_times[(job2, machine)]
                    
                    # Either job1 finishes before job2 starts, or job2 finishes before job1 starts
                    # This is implemented as: start1 + time1 <= start2 OR start2 + time2 <= start1
                    # We need to use a disjunctive constraint or binary variables
                    
                    # Create binary variable for precedence
                    prec_var = ORToolsVariable(
                        name=f"prec_{job1}_{job2}_{machine}",
                        domain=[0, 1],
                        var_type="binary"
                    )
                    problem.add_variable(prec_var)
                    
                    # If prec_var = 1, then job1 before job2
                    problem.add_constraint(ORToolsConstraint(
                        name=f"prec1_{job1}_{job2}_{machine}",
                        constraint_type="less_equal",
                        variables=[start1, start2, prec_var],
                        coefficients=[1, -1, 1000],
                        constant=time1 - 1000
                    ))
                    
                    # If prec_var = 0, then job2 before job1
                    problem.add_constraint(ORToolsConstraint(
                        name=f"prec2_{job1}_{job2}_{machine}",
                        constraint_type="less_equal",
                        variables=[start2, start1, prec_var],
                        coefficients=[1, -1, -1000],
                        constant=time2
                    ))
    
    # Solve the problem
    solution = solve_problem(problem)
    
    if solution.is_optimal:
        result = {
            'makespan': solution.variable_values['makespan'],
            'schedule': {}
        }
        
        for (job, machine), start_var in start_times.items():
            start_time = solution.variable_values[f"start_{job}_{machine}"]
            processing_time = processing_times[(job, machine)]
            result['schedule'][(job, machine)] = {
                'start': start_time,
                'end': start_time + processing_time,
                'duration': processing_time
            }
        
        return result
    else:
        return None

def visualize_schedule(schedule, jobs, machines, processing_times):
    """Visualize the job shop schedule as a Gantt chart"""
    
    # Prepare data for Gantt chart
    gantt_data = []
    for (job, machine), info in schedule.items():
        gantt_data.append({
            'Job': job,
            'Machine': machine,
            'Start': info['start'],
            'Duration': info['duration'],
            'End': info['end']
        })
    
    df = pd.DataFrame(gantt_data)
    
    # Create Gantt chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(jobs)))
    job_colors = {job: colors[i] for i, job in enumerate(jobs)}
    
    y_pos = 0
    machine_positions = {}
    
    for machine in machines:
        machine_positions[machine] = y_pos
        y_pos += 1
    
    for _, row in df.iterrows():
        job = row['Job']
        machine = row['Machine']
        start = row['Start']
        duration = row['Duration']
        
        y_pos = machine_positions[machine]
        
        # Draw rectangle
        rect = plt.Rectangle((start, y_pos - 0.4), duration, 0.8, 
                           facecolor=job_colors[job], alpha=0.7, edgecolor='black')
        ax.add_patch(rect)
        
        # Add job label
        ax.text(start + duration/2, y_pos, job, ha='center', va='center', 
                fontweight='bold', fontsize=8)
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Machine')
    ax.set_yticks(range(len(machines)))
    ax.set_yticklabels(machines)
    ax.set_title('Job Shop Schedule (Gantt Chart)')
    ax.grid(True, alpha=0.3)
    
    # Add legend
    legend_elements = [plt.Rectangle((0, 0), 1, 1, facecolor=job_colors[job], alpha=0.7) 
                      for job in jobs]
    ax.legend(legend_elements, jobs, loc='upper right')
    
    plt.tight_layout()
    plt.show()

def generate_job_shop_data(n_jobs=5, n_machines=3):
    """Generate random job shop scheduling data"""
    np.random.seed(42)
    
    jobs = [f"Job_{i+1}" for i in range(n_jobs)]
    machines = [f"Machine_{i+1}" for i in range(n_machines)]
    
    # Each job must visit each machine exactly once
    processing_times = {}
    for job in jobs:
        # Random order of machines for each job
        machine_order = np.random.permutation(machines)
        for machine in machine_order:
            processing_times[(job, machine)] = np.random.randint(1, 10)
    
    return jobs, machines, processing_times

def analyze_scheduling_performance():
    """Analyze performance for different problem sizes"""
    sizes = [(3, 3), (5, 3), (5, 5), (8, 4)]
    solve_times = []
    makespans = []
    
    for n_jobs, n_machines in sizes:
        print(f"Solving {n_jobs} jobs on {n_machines} machines...")
        
        jobs, machines, processing_times = generate_job_shop_data(n_jobs, n_machines)
        
        import time
        start_time = time.time()
        solution = solve_job_shop_scheduling(jobs, machines, processing_times)
        end_time = time.time()
        
        solve_time = end_time - start_time
        solve_times.append(solve_time)
        
        if solution:
            makespans.append(solution['makespan'])
            print(f"  Makespan: {solution['makespan']}, Time: {solve_time:.3f}s")
        else:
            makespans.append(0)
            print(f"  No solution found, Time: {solve_time:.3f}s")
    
    # Plot performance
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    problem_sizes = [f"{n_jobs}×{n_machines}" for n_jobs, n_machines in sizes]
    
    ax1.plot(problem_sizes, solve_times, 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('Problem Size (Jobs × Machines)')
    ax1.set_ylabel('Solve Time (seconds)')
    ax1.set_title('Job Shop Scheduling Solve Time')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(problem_sizes, makespans, 'go-', linewidth=2, markersize=8)
    ax2.set_xlabel('Problem Size (Jobs × Machines)')
    ax2.set_ylabel('Makespan')
    ax2.set_title('Optimal Makespan')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("Job Shop Scheduling Problem Solver")
    print("=" * 50)
    
    # Generate sample data
    jobs, machines, processing_times = generate_job_shop_data(5, 3)
    
    print(f"Jobs: {jobs}")
    print(f"Machines: {machines}")
    print(f"Processing times: {processing_times}")
    
    # Solve the problem
    print("\nSolving job shop scheduling problem...")
    solution = solve_job_shop_scheduling(jobs, machines, processing_times)
    
    if solution:
        print(f"Optimal makespan: {solution['makespan']}")
        print("\nSchedule:")
        for (job, machine), info in solution['schedule'].items():
            print(f"  {job} on {machine}: {info['start']}-{info['end']} (duration: {info['duration']})")
        
        print("\nVisualizing schedule...")
        visualize_schedule(solution['schedule'], jobs, machines, processing_times)
    else:
        print("No solution found!")
    
    print("\nPerformance Analysis:")
    analyze_scheduling_performance()
