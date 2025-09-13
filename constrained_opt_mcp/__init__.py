"""
Constrained Optimization MCP Server

A general-purpose Model Context Protocol server for solving combinatorial 
optimization problems with logical and numerical constraints.

This package provides a unified interface to multiple optimization solvers:
- Z3: SMT solver for logical constraints
- CVXPY: Convex optimization
- HiGHS: Linear and mixed-integer programming
- OR-Tools: Constraint programming and combinatorial optimization

The server exposes these capabilities through MCP tools that can be used
by AI assistants to solve complex optimization problems.
"""

__version__ = "1.0.0"
__author__ = "Rajnish Sharma"

from .core.problem_types import ProblemType, OptimizationSense
from .core.base_models import BaseProblem, BaseSolution, BaseVariable, BaseConstraint
from .models import (
    Z3Problem, Z3Solution, Z3Variable, Z3Constraint,
    CVXPYProblem, CVXPYSolution, CVXPYVariable, CVXPYConstraint,
    HiGHSProblem, HiGHSSolution, HiGHSVariable, HiGHSConstraint,
    ORToolsProblem, ORToolsSolution, ORToolsVariable, ORToolsConstraint
)

__all__ = [
    # Core types
    "ProblemType",
    "OptimizationSense", 
    "BaseProblem",
    "BaseSolution",
    "BaseVariable",
    "BaseConstraint",
    
    # Z3 models
    "Z3Problem",
    "Z3Solution", 
    "Z3Variable",
    "Z3Constraint",
    
    # CVXPY models
    "CVXPYProblem",
    "CVXPYSolution",
    "CVXPYVariable", 
    "CVXPYConstraint",
    
    # HiGHS models
    "HiGHSProblem",
    "HiGHSSolution",
    "HiGHSVariable",
    "HiGHSConstraint",
    
    # OR-Tools models
    "ORToolsProblem",
    "ORToolsSolution", 
    "ORToolsVariable",
    "ORToolsConstraint",
]
