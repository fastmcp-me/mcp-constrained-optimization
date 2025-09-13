<p align="center">
    <img src=".github/logo.png" width="500px" alt="Constrained Optimization MCP Server">
</p>

# Constrained Optimization MCP Server

A general-purpose Model Context Protocol (MCP) server for solving combinatorial optimization problems with logical and numerical constraints. This server provides a unified interface to multiple optimization solvers, enabling AI assistants to solve complex optimization problems across various domains.

## 🚀 Features

- **Unified Interface**: Single MCP server for multiple optimization backends
- **AI-Ready**: Designed for use with AI assistants through MCP protocol
- **Portfolio Focus**: Specialized tools for portfolio optimization and risk management
- **Extensible**: Modular design for easy addition of new solvers
- **High Performance**: Optimized for large-scale problems
- **Robust**: Comprehensive error handling and validation

## 🛠️ Supported Solvers

* [`Z3`](https://github.com/Z3Prover/z3) - SMT solver for constraint satisfaction problems
* [`CVXPY`](https://www.cvxpy.org/) - Convex optimization solver
* [`HiGHS`](https://highs.dev/) - Linear and mixed-integer programming solver
* [`OR-Tools`](https://developers.google.com/optimization) - Constraint programming solver

## 📦 Installation

```bash
# Install the package
pip install constrained-opt-mcp

# Or install from source
git clone https://github.com/your-org/constrained-opt-mcp
cd constrained-opt-mcp
pip install -e .
```

## 📐 Mathematical Foundations

### Optimization Theory

The Constrained Optimization MCP Server implements solutions for various classes of optimization problems:

#### **Linear Programming (LP)**
$$\min_{x} c^T x \quad \text{subject to} \quad Ax \leq b, \quad x \geq 0$$

#### **Quadratic Programming (QP)**
$$\min_{x} \frac{1}{2}x^T Q x + c^T x \quad \text{subject to} \quad Ax \leq b, \quad x \geq 0$$

#### **Convex Optimization**
$$\min_{x} f(x) \quad \text{subject to} \quad g_i(x) \leq 0, \quad h_j(x) = 0$$

Where $f$ and $g_i$ are convex functions.

#### **Constraint Satisfaction Problems (CSP)**
Find $x \in \mathcal{D}$ such that $C_1(x) \land C_2(x) \land \ldots \land C_k(x)$

#### **Portfolio Optimization (Markowitz)**
$$\max_{w} \mu^T w - \frac{\lambda}{2} w^T \Sigma w \quad \text{subject to} \quad \sum_{i=1}^{n} w_i = 1, \quad w_i \geq 0$$

Where:
- $w$: portfolio weights
- $\mu$: expected returns
- $\Sigma$: covariance matrix
- $\lambda$: risk aversion parameter

### Solver Capabilities

| Problem Type | Solver | Complexity | Mathematical Form |
|--------------|--------|------------|-------------------|
| Constraint Satisfaction | Z3 | NP-Complete | Logical constraints |
| Convex Optimization | CVXPY | Polynomial | Convex functions |
| Linear Programming | HiGHS | Polynomial | Linear constraints |
| Constraint Programming | OR-Tools | NP-Complete | Discrete domains |

## 🚀 Quick Start

### 1. Run Examples

```bash
# Run individual examples
python examples/nqueens.py
python examples/knapsack.py
python examples/portfolio_optimization.py
python examples/job_shop_scheduling.py
python examples/nurse_scheduling.py
python examples/economic_production_planning.py

# Run interactive notebook
jupyter notebook examples/constrained_optimization_demo.ipynb
```

### 2. Start the MCP Server

```bash
constrained-opt-mcp
```

### 3. Connect from AI Assistant

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

### 4. Use the Tools

The server provides the following tools:

- `solve_constraint_satisfaction` - Solve logical constraint problems
- `solve_convex_optimization` - Solve convex optimization problems  
- `solve_linear_programming` - Solve linear programming problems
- `solve_constraint_programming` - Solve constraint programming problems
- `solve_portfolio_optimization` - Solve portfolio optimization problems

## 📚 Examples

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

### Portfolio Examples

- **[Portfolio Optimization](constrained_opt_mcp/examples/financial/portfolio_optimization.py)** - Advanced portfolio optimization strategies including Markowitz, Black-Litterman, and ESG-constrained optimization
- **[Risk Management](constrained_opt_mcp/examples/financial/risk_management.py)** - Risk management strategies including VaR optimization, stress testing, and hedging

#### Enhanced Portfolio Optimization Features

**Equity Portfolio Optimization:**
- Sector diversification constraints (max 25% per sector)
- Market cap constraints (large, mid, small cap allocations)
- ESG (Environmental, Social, Governance) constraints
- Liquidity requirements and individual position limits
- Risk-return optimization with advanced metrics

**Multi-Asset Portfolio Optimization:**
- Asset class constraints (equity, fixed income, alternatives, cash)
- Regional exposure limits (developed vs emerging markets)
- Alternative investment constraints (commodities, real estate, private equity)
- Dynamic rebalancing and risk budgeting
- Multi-period optimization with transaction costs

**Advanced Risk Metrics:**
- Value at Risk (VaR) and Conditional VaR (CVaR)
- Maximum Drawdown and Tail Risk
- Factor exposure analysis and risk attribution
- Stress testing and scenario analysis
- Correlation and concentration risk management

### Comprehensive Examples

#### 🎯 **Combinatorial Optimization**
- **[N-Queens Problem](examples/nqueens.py)** - Classic constraint satisfaction with chessboard visualization
- **[Knapsack Problem](examples/knapsack.py)** - 0/1 and multiple knapsack variants with performance analysis

#### 🏭 **Scheduling & Operations**
- **[Job Shop Scheduling](examples/job_shop_scheduling.py)** - Multi-machine production scheduling with Gantt charts
- **[Nurse Scheduling](examples/nurse_scheduling.py)** - Complex workforce scheduling with fairness constraints

#### 📊 **Quantitative Economics & Finance**
- **[Portfolio Optimization](examples/portfolio_optimization.py)** - Advanced strategies including Markowitz, Black-Litterman, Risk Parity, and ESG-constrained optimization
- **[Economic Production Planning](examples/economic_production_planning.py)** - Multi-period supply chain optimization with inventory management

#### 🧮 **Interactive Learning**
- **[Comprehensive Demo Notebook](examples/constrained_optimization_demo.ipynb)** - Interactive Jupyter notebook with all solver types and visualizations

## 🧪 Testing

Run the comprehensive test suite:

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

## 📖 Documentation

- **[API Reference](docs/README.md)** - Complete API documentation
- **[Examples](examples/)** - Comprehensive examples and demos
- **[Jupyter Notebook](examples/constrained_optimization_demo.ipynb)** - Interactive demo notebook
- **[PDF Documentation](docs/constrained_optimization_package.pdf)** - Comprehensive PDF guide with theory, examples, and implementation details
- **[Journal-Style PDF](docs/constrained_optimization_journal.pdf)** - Academic paper format with literature review, mathematics, and research contributions

## 🏗️ Architecture

### Core Components

1. **Core Models** (`constrained_opt_mcp/core/`) - Base classes and problem types
2. **Solver Models** (`constrained_opt_mcp/models/`) - Problem-specific model definitions  
3. **Solvers** (`constrained_opt_mcp/solvers/`) - Solver implementations
4. **MCP Server** (`constrained_opt_mcp/server/`) - MCP server implementation
5. **Examples** (`constrained_opt_mcp/examples/`) - Usage examples and demos

### Supported Problem Types

| Problem Type | Solver | Use Cases |
|--------------|--------|-----------|
| Constraint Satisfaction | Z3 | Logic puzzles, verification, planning |
| Convex Optimization | CVXPY | Portfolio optimization, machine learning |
| Linear Programming | HiGHS | Production planning, resource allocation |
| Constraint Programming | OR-Tools | Scheduling, assignment, routing |
| Portfolio Optimization | Multiple | Risk management, portfolio construction |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## 🆘 Support

For questions, issues, or contributions, please:

1. Check the [documentation](docs/)
2. Search [existing issues](https://github.com/your-org/constrained-opt-mcp/issues)
3. Create a [new issue](https://github.com/your-org/constrained-opt-mcp/issues/new)
4. Join our [discussions](https://github.com/your-org/constrained-opt-mcp/discussions)

## 📈 Changelog

### Version 1.0.0
- Initial release
- Support for Z3, CVXPY, HiGHS, and OR-Tools
- Portfolio optimization examples
- Comprehensive test suite
- MCP server implementation
