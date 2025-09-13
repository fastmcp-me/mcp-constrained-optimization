"""
Problem type definitions for the constrained optimization MCP server.
"""

from enum import Enum
from typing import Union


class ProblemType(str, Enum):
    """Types of optimization problems supported by the MCP server."""
    
    # Constraint satisfaction problems
    CONSTRAINT_SATISFACTION = "constraint_satisfaction"
    
    # Linear programming
    LINEAR_PROGRAMMING = "linear_programming"
    MIXED_INTEGER_LINEAR = "mixed_integer_linear"
    
    # Convex optimization
    CONVEX_OPTIMIZATION = "convex_optimization"
    QUADRATIC_PROGRAMMING = "quadratic_programming"
    SECOND_ORDER_CONE = "second_order_cone"
    SEMIDEFINITE_PROGRAMMING = "semidefinite_programming"
    
    # Combinatorial optimization
    COMBINATORIAL_OPTIMIZATION = "combinatorial_optimization"
    CONSTRAINT_PROGRAMMING = "constraint_programming"
    INTEGER_PROGRAMMING = "integer_programming"
    
    # Specialized problem types
    NETWORK_FLOW = "network_flow"
    SCHEDULING = "scheduling"
    ASSIGNMENT = "assignment"
    ROUTING = "routing"
    PACKING = "packing"
    CUTTING_STOCK = "cutting_stock"
    
    # Financial optimization
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    RISK_MANAGEMENT = "risk_management"
    ASSET_ALLOCATION = "asset_allocation"
    DERIVATIVES_PRICING = "derivatives_pricing"


class OptimizationSense(str, Enum):
    """Optimization objective sense."""
    
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
    SATISFY = "satisfy"  # For constraint satisfaction problems


class SolverType(str, Enum):
    """Available solver backends."""
    
    Z3 = "z3"
    CVXPY = "cvxpy"
    HIGHS = "highs"
    ORTOOLS = "ortools"


class VariableType(str, Enum):
    """Variable types in optimization problems."""
    
    # Continuous variables
    CONTINUOUS = "continuous"
    REAL = "real"
    
    # Discrete variables
    INTEGER = "integer"
    BINARY = "binary"
    BOOLEAN = "boolean"
    
    # Specialized types
    STRING = "string"
    CATEGORICAL = "categorical"
    ORDINAL = "ordinal"


class ConstraintType(str, Enum):
    """Types of constraints in optimization problems."""
    
    # Linear constraints
    LINEAR_EQUALITY = "linear_equality"
    LINEAR_INEQUALITY = "linear_inequality"
    
    # Quadratic constraints
    QUADRATIC = "quadratic"
    SECOND_ORDER_CONE = "second_order_cone"
    
    # Logical constraints
    LOGICAL = "logical"
    IMPLICATION = "implication"
    DISJUNCTION = "disjunction"
    
    # Specialized constraints
    BOUNDS = "bounds"
    CARDINALITY = "cardinality"
    ALL_DIFFERENT = "all_different"
    ELEMENT = "element"
    TABLE = "table"
    
    # Financial constraints
    RISK_BUDGET = "risk_budget"
    CONCENTRATION_LIMIT = "concentration_limit"
    TURNOVER_LIMIT = "turnover_limit"
