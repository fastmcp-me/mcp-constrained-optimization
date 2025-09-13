# Constrained Optimization MCP Server

A general-purpose Model Context Protocol (MCP) server for solving combinatorial optimization problems with logical and numerical constraints.

## Overview

The Constrained Optimization MCP Server provides a unified interface to multiple optimization solvers, enabling AI assistants to solve complex optimization problems across various domains including:

- **Constraint Satisfaction Problems** (Z3 SMT solver)
- **Convex Optimization** (CVXPY)
- **Linear and Mixed-Integer Programming** (HiGHS)
- **Constraint Programming** (OR-Tools)
- **Portfolio Optimization** (Markowitz, Black-Litterman, Risk Parity, ESG-constrained)
- **Scheduling & Operations** (Job shop scheduling, nurse scheduling, resource allocation)
- **Combinatorial Optimization** (N-Queens, knapsack problems, assignment)
- **Economic Production Planning** (Multi-period planning, inventory management)

## Features

- 🚀 **Unified Interface**: Single MCP server for multiple optimization backends
- 🧠 **AI-Ready**: Designed for use with AI assistants through MCP protocol
- 📊 **Comprehensive Examples**: Extensive examples across multiple domains
- 🎯 **Combinatorial Optimization**: N-Queens, knapsack, and assignment problems
- 🏭 **Scheduling & Operations**: Job shop and nurse scheduling with visualizations
- 💰 **Portfolio Optimization**: Advanced financial strategies and risk management
- 🏭 **Economic Planning**: Multi-period production planning and supply chain optimization
- 🔧 **Extensible**: Modular design for easy addition of new solvers
- 📈 **High Performance**: Optimized for large-scale problems
- 🛡️ **Robust**: Comprehensive error handling and validation

## Installation

```bash
# Install the package
pip install constrained-opt-mcp

# Or install from source
git clone https://github.com/your-org/constrained-opt-mcp
cd constrained-opt-mcp
pip install -e .
```

## Quick Start

### 1. Start the MCP Server

```bash
constrained-opt-mcp
```

### 2. Connect from AI Assistant

Add the server to your MCP configuration:

```json
{
  "mcpServers": {
    "constrained-opt-mcp": {
      "command": "constrained-opt-mcp",
      "args": []
    }
  }
}
```

### 3. Use the Tools

The server provides the following tools:

- `solve_constraint_satisfaction`: Solve logical constraint problems
- `solve_convex_optimization`: Solve convex optimization problems
- `solve_linear_programming`: Solve linear programming problems
- `solve_constraint_programming`: Solve constraint programming problems
- `solve_portfolio_optimization`: Solve portfolio optimization problems

## Comprehensive Examples

### 🎯 Combinatorial Optimization

#### N-Queens Problem (`examples/nqueens.py`)
- Classic constraint satisfaction problem
- Chessboard visualization of solutions
- Performance analysis across board sizes
- OR-Tools constraint programming

#### Knapsack Problem (`examples/knapsack.py`)
- 0/1 and multiple knapsack variants
- Binary decision variables
- Value maximization under constraints
- Performance analysis and visualization

### 🏭 Scheduling & Operations

#### Job Shop Scheduling (`examples/job_shop_scheduling.py`)
- Multi-machine production scheduling
- Makespan minimization
- Gantt chart visualization
- Resource allocation constraints

#### Nurse Scheduling (`examples/nurse_scheduling.py`)
- Complex workforce scheduling
- Shift coverage and fairness constraints
- Nurse preferences and soft constraints
- Schedule quality analysis

### 📊 Portfolio Optimization

#### Advanced Portfolio Optimization (`examples/portfolio_optimization.py`)
- Markowitz mean-variance optimization
- Black-Litterman model with investor views
- Risk parity optimization
- ESG-constrained optimization
- Efficient frontier analysis
- Strategy comparison and visualization

### 🏭 Economic Production Planning

#### Multi-Period Production Planning (`examples/economic_production_planning.py`)
- Multi-period production planning
- Inventory management and demand forecasting
- Cost minimization strategies
- Resource allocation and capacity constraints
- Strategy comparison (JIT vs Safety Stock vs Balanced)

### 🧮 Interactive Learning

#### Comprehensive Demo Notebook (`examples/constrained_optimization_demo.ipynb`)
- Interactive Jupyter notebook
- All solver types with examples
- Real-time visualizations
- Mathematical theory and formulations
- Performance analysis

## Examples

### Constraint Satisfaction Problem

```python
# Solve a simple arithmetic constraint problem
variables = [
    {"name": "x", "type": "integer"},
    {"name": "y", "type": "integer"},
]
constraints = [
    "x + y == 10",
    "x - y == 2",
]

# Result: x=6, y=4
```

### Portfolio Optimization

```python
# Optimize portfolio allocation
assets = ["Stocks", "Bonds", "Real Estate", "Commodities"]
expected_returns = [0.10, 0.03, 0.07, 0.06]
risk_factors = [0.15, 0.03, 0.12, 0.20]
correlation_matrix = [
    [1.0, 0.2, 0.6, 0.3],
    [0.2, 1.0, 0.1, 0.05],
    [0.6, 0.1, 1.0, 0.25],
    [0.3, 0.05, 0.25, 1.0],
]

# Result: Optimal portfolio weights and performance metrics
```

### Linear Programming

```python
# Production planning problem
sense = "maximize"
objective_coeffs = [3.0, 2.0]  # Profit per unit
variables = [
    {"name": "product_a", "lb": 0, "ub": None, "type": "cont"},
    {"name": "product_b", "lb": 0, "ub": None, "type": "cont"},
]
constraint_matrix = [
    [2, 1],  # Labor: 2*A + 1*B <= 100
    [1, 2],  # Material: 1*A + 2*B <= 80
]
constraint_senses = ["<=", "<="]
rhs_values = [100.0, 80.0]

# Result: Optimal production quantities
```

## Architecture

### Core Components

1. **Core Models** (`constrained_opt_mcp/core/`): Base classes and problem types
2. **Solver Models** (`constrained_opt_mcp/models/`): Problem-specific model definitions
3. **Solvers** (`constrained_opt_mcp/solvers/`): Solver implementations
4. **MCP Server** (`constrained_opt_mcp/server/`): MCP server implementation
5. **Examples** (`constrained_opt_mcp/examples/`): Usage examples and demos

### Supported Problem Types

| Problem Type | Solver | Use Cases |
|--------------|--------|-----------|
| Constraint Satisfaction | Z3 | Logic puzzles, verification, planning |
| Convex Optimization | CVXPY | Portfolio optimization, machine learning |
| Linear Programming | HiGHS | Production planning, resource allocation |
| Constraint Programming | OR-Tools | Scheduling, assignment, routing |
| Financial Optimization | Multiple | Risk management, portfolio construction |

## API Reference

### Core Types

#### ProblemType
```python
class ProblemType(str, Enum):
    CONSTRAINT_SATISFACTION = "constraint_satisfaction"
    LINEAR_PROGRAMMING = "linear_programming"
    CONVEX_OPTIMIZATION = "convex_optimization"
    COMBINATORIAL_OPTIMIZATION = "combinatorial_optimization"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    # ... more types
```

#### OptimizationSense
```python
class OptimizationSense(str, Enum):
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
    SATISFY = "satisfy"
```

### MCP Tools

#### solve_constraint_satisfaction
Solve constraint satisfaction problems using Z3.

**Parameters:**
- `variables`: List of variable definitions
- `constraints`: List of constraint expressions
- `description`: Optional problem description
- `timeout`: Optional timeout in milliseconds

**Returns:**
- Solution values and satisfiability status

#### solve_convex_optimization
Solve convex optimization problems using CVXPY.

**Parameters:**
- `variables`: List of variable definitions
- `objective_type`: "minimize" or "maximize"
- `objective_expr`: Objective function expression
- `constraints`: List of constraint expressions
- `parameters`: Optional parameter values
- `description`: Optional problem description

**Returns:**
- Optimal solution and objective value

#### solve_linear_programming
Solve linear programming problems using HiGHS.

**Parameters:**
- `sense`: "minimize" or "maximize"
- `objective_coeffs`: Objective function coefficients
- `variables`: List of variable definitions
- `constraint_matrix`: Constraint matrix
- `constraint_senses`: Constraint directions
- `rhs_values`: Right-hand side values
- `options`: Optional solver options
- `description`: Optional problem description

**Returns:**
- Optimal solution and objective value

#### solve_constraint_programming
Solve constraint programming problems using OR-Tools.

**Parameters:**
- `variables`: List of variable definitions
- `constraints`: List of constraint expressions
- `objective`: Optional objective definition
- `parameters`: Optional solver parameters
- `description`: Optional problem description

**Returns:**
- Solution values and feasibility status

#### solve_portfolio_optimization
Solve portfolio optimization problems using modern portfolio theory.

**Parameters:**
- `assets`: List of asset names
- `expected_returns`: Expected returns for each asset
- `risk_factors`: Risk factors (standard deviations)
- `correlation_matrix`: Correlation matrix between assets
- `max_allocations`: Optional maximum allocation limits
- `risk_budget`: Optional maximum portfolio risk
- `description`: Optional problem description

**Returns:**
- Optimal portfolio weights and performance metrics

## Financial Examples

### Portfolio Optimization

```python
from constrained_opt_mcp.examples.financial.portfolio_optimization import PortfolioOptimizer

# Create optimizer
optimizer = PortfolioOptimizer(assets, expected_returns, risk_factors, correlation_matrix)

# Markowitz optimization
result = optimizer.markowitz_optimization(risk_budget=0.01)

# ESG-constrained optimization
result = optimizer.esg_constrained_optimization(esg_scores, min_esg_score=0.7)

# Black-Litterman optimization
result = optimizer.black_litterman_optimization(market_caps)
```

### Risk Management

```python
from constrained_opt_mcp.examples.financial.risk_management import RiskManager

# Create risk manager
risk_manager = RiskManager(assets, returns_data)

# VaR optimization
result = risk_manager.var_optimization(confidence_level=0.05, max_var=0.02)

# CVaR optimization
result = risk_manager.cvar_optimization(confidence_level=0.05, max_cvar=0.03)

# Stress testing
results = risk_manager.stress_testing(stress_scenarios)
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_z3_solver.py
pytest tests/test_cvxpy_solver.py
pytest tests/test_highs_solver.py
pytest tests/test_ortools_solver.py
pytest tests/test_mcp_server.py

# Run with coverage
pytest --cov=constrained_opt_mcp
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or contributions, please:

1. Check the [documentation](docs/)
2. Search [existing issues](https://github.com/your-org/constrained-opt-mcp/issues)
3. Create a [new issue](https://github.com/your-org/constrained-opt-mcp/issues/new)
4. Join our [discussions](https://github.com/your-org/constrained-opt-mcp/discussions)

## Changelog

### Version 1.0.0
- Initial release
- Support for Z3, CVXPY, HiGHS, and OR-Tools
- Financial optimization examples
- Comprehensive test suite
- MCP server implementation
