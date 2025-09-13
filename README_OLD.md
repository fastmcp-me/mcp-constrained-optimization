<p align="center">
    <img src=".github/logo.png" width="500px" alt="Constrained Optimization MCP Server">
</p>

# Constrained Optimization MCP Server

A general-purpose Model Context Protocol (MCP) server for solving combinatorial optimization problems with logical and numerical constraints. This server provides a unified interface to multiple optimization solvers, enabling AI assistants to solve complex optimization problems across various domains.

## 🚀 Features

- **Unified Interface**: Single MCP server for multiple optimization backends
- **AI-Ready**: Designed for use with AI assistants through MCP protocol
- **Financial Focus**: Specialized tools for portfolio optimization and risk management
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

## 🚀 Quick Start

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

### Financial Examples

- **[Portfolio Optimization](constrained_opt_mcp/examples/financial/portfolio_optimization.py)** - Advanced portfolio optimization strategies including Markowitz, Black-Litterman, and ESG-constrained optimization
- **[Risk Management](constrained_opt_mcp/examples/financial/risk_management.py)** - Risk management strategies including VaR optimization, stress testing, and hedging

### Classic Examples

- **[Chemical Engineering](examples/chemical_engineering.py)** - Pipeline design optimization using Z3 SMT solver
- **[Job Shop Scheduling](examples/job_shop.py)** - Complex scheduling problem using OR-Tools
- **[Nurse Scheduling](examples/nurse_scheduling.py)** - Hospital staff scheduling using OR-Tools
- **[Coin Problem](examples/coin_problem.py)** - Classic logic puzzle using Z3
- **[N-Queens](examples/nqueens.py)** - Place N queens on an N×N chessboard using OR-Tools

### Logic Puzzle

```
You and a friend pass by a standard coin operated vending machine and you decide to get a candy bar.
The price is US $0.95, but after checking your pockets you only have a dollar (US $1) and the machine
only takes coins. You turn to your friend and have this conversation:

You: Hey, do you have change for a dollar?
Friend: Let's see. I have 6 US coins but, although they add up to a US $1.15, I can't break a dollar.
You: Huh? Can you make change for half a dollar?
Friend: No.
You: How about a quarter?
Friend: Nope, and before you ask I cant make change for a dime or nickel either.
You: Really? and these six coins are all US government coins currently in production?
Friend: Yes.
You: Well can you just put your coins into the vending machine and buy me a candy bar, and I'll pay you back?
Friend: Sorry, I would like to but I can't with the coins I have.

What coins are your friend holding?
```

This can be fed into usolver and it will generate a constraint system:

$C$ is the collection of the six unknown coin values, $c_1$ through $c_6$, each of which must be a positive whole number representing cents.

$$
C = \\{c_1, c_2, c_3, c_4, c_5, c_6\\}, \quad \text{where each } c_i \in \mathbb{Z}^+
$$

$\mathcal{S}$ is the collection of every possible way you could choose two or more of your six coins.

$$
\mathcal{S} = \\{S \mid S \subseteq C \land |S| \ge 2 \\}
$$

Exclude the 50 cent coin from being used in the vending machine.

$$
v(x) = \begin{cases} 0 & \text{if } x = 50 \\\\ x & \text{if } x \neq 50 \end{cases}
$$

Constraint 0: The sum of the values of all six coins is 115 cents.

$$
\sum_{i=1}^{6} c_i = 115
$$

Constraint 1: Cannot make change for a dollar.

$$
\forall S \in \mathcal{S}, \quad \sum_{x \in S} x \neq 100
$$

Constraint 2: Cannot make change for half a dollar.

$$
\forall S \in \mathcal{S}, \quad \sum_{x \in S} x \neq 50
$$

Constraint 3: Cannot make change for a quarter.

$$
\forall S \in \mathcal{S}, \quad \sum_{x \in S} x \neq 25
$$

Constraint 4: Cannot make change for a dime.

$$
\forall S \in \mathcal{S}, \quad \sum_{x \in S} x \neq 10
$$

Constraint 5: Cannot make change for a nickel

$$
\forall S \in \mathcal{S}, \quad \sum_{x \in S} x \neq 5
$$

Constraint 6: Cannot buy the candy bar for 95 cents if half dollar is excluded.

$$
\forall S \in \mathcal{S}, \quad \sum_{x \in S} v(x) \neq 95
$$

If you feed this to solver it will synthesize the above constraint system, solve it with Z3, and return the solution.

```markdown
Your friend has: 1 half dollar, 1 quarter, and 4 dimes
This totals 50¢ + 25¢ + 40¢ = 115¢ = $1.15 ✓
This is exactly 6 coins ✓
```

### Modern Portfolio Theory

A finance example:

```markdown
Objective: Maximize expected portfolio return
Constraints:

Bonds allocation cannot exceed 40%
Stocks allocation cannot exceed 60%
Real Estate allocation cannot exceed 30%
Commodities allocation cannot exceed 20%
All allocations must be non-negative
Total allocation must equal exactly 100%
Total weighted portfolio risk cannot exceed 10%

Given Data:

Expected returns: Bonds 8%, Stocks 12%, Real Estate 10%, Commodities 15%
Risk factors: Bonds 2%, Stocks 15%, Real Estate 8%, Commodities 20%
```

This is compiled by the langauge model down into a convex optimization problem that can be cvxopt.

$$
\begin{align}
\text{maximize} \quad & 0.08x_1 + 0.12x_2 + 0.10x_3 + 0.15x_4 \\
\text{subject to} \quad & x_1 + x_2 + x_3 + x_4 = 1 \\
& x_1 \leq 0.4 \\
& x_2 \leq 0.6 \\
& x_3 \leq 0.3 \\
& x_4 \leq 0.2 \\
& 0.02x_1 + 0.15x_2 + 0.08x_3 + 0.20x_4 \leq 0.10 \\
& x_1, x_2, x_3, x_4 \geq 0
\end{align}
$$

Where:
- $x_1$ = Bonds allocation
- $x_2$ = Stocks allocation
- $x_3$ = Real Estate allocation
- $x_4$ = Commodities allocation

The answer is then:

```markdown
Bonds: 30.0%
Stocks: 20.0%
Real Estate: 30.0% (at maximum allowed)
Commodities: 20.0% (at maximum allowed)
Maximum Expected Return: 10.8% annually
```

### Z3

A chemical engineering example:

```markdown
Use usolver to design a water transport pipeline with the following requirements:

* Volumetric flow rate: 0.05 m³/s
* Pipe length: 100 m
* Water density: 1000 kg/m³
* Maximum allowable pressure drop: 50 kPa
* Flow continuity: Q = π(D/2)² × v
* Pressure drop: ΔP = f(L/D)(ρv²/2), where f ≈ 0.02 for turbulent flow
* Practical limits: 0.05 ≤ D ≤ 0.5 m, 0.5 ≤ v ≤ 8 m/s
* Pressure constraint: ΔP ≤ 50,000 Pa
* Find: optimal pipe diameter and flow velocity
```

### Linear Programming

A multilinear optimization example:

```markdown
Use usolver to solve the following linear programming problem:

Minimize: 12x + 20y
Subject to: 6x + 8y ≥ 100
           7x + 12y ≥ 120
           x ≥ 0
           y ∈ [0, 3]
```

This is compiled by the language model down into a constraint satisfaction problem that can be solved with Z3.

$$
\begin{aligned}
\text{minimize} \quad & 12x + 20y \\
\text{subject to} \quad & 6x + 8y \geq 100 \\
& 7x + 12y \geq 120 \\
& x \geq 0 \\
& y \in [0, 3]
\end{aligned}
$$

Where:
- $x$ = First decision variable (continuous, non-negative)
- $y$ = Second decision variable (continuous, bounded)

The optimal solution is:

```markdown
x = 15.0
y = 1.25
Objective value = 205.0
```

### CVXPY

A simple convex optimization problem minimizing the 2-norm of a linear system:

```markdown
Use usolver to solve the following convex optimization problem:

Minimize: ||Ax - b||₂²
Subject to: 0 ≤ x ≤ 1
where 
  A = [1.0, -0.5; 0.5, 2.0; 0.0, 1.0] 
  b = [2.0, 1.0, -1.0]
```

### OR-Tools

A classic worker shift scheduling problem:

```markdown
Use usolver to solve a nurse scheduling problem with the following requirements:

* Schedule 4 nurses (Alice, Bob, Charlie, Diana) across 3 shifts over (Monday, Tuesday, Wednesday)
* Shifts: Morning (7AM-3PM), Evening (3PM-11PM), Night (11PM-7AM)
* Each shift must be assigned to exactly one nurse each day
* Each nurse works at most one shift per day
* Distribute shifts evenly (2-3 shifts per nurse over the period)
* Charlie can't work on Tuesday.
```

### Chained Examples

A chained example that uses both OR-Tools to optimize for table layout and CVXPY to optimize for staff scheduling.

```markdown
Use usolver to optimize a restaurant's layout and staffing with the following requirements in two parts. Use combinatorial optimization to optimize for table layout and convex optimization to optimize for staff scheduling.

* Part 1: Optimize table layout
  - Mix of 2-seater, 4-seater, and 6-seater tables
  - Maximum floor space: 150 m²
  - Space requirements: 4m² (2-seater), 6m² (4-seater), 9m² (6-seater)
  - Maximum 20 tables total
  - Minimum mix: 2× 2-seaters, 3× 4-seaters, 1× 6-seater
  - Objective: Maximize total seating capacity

* Part 2: Optimize staff scheduling using Part 1's capacity
  - 12-hour operating day
  - Each staff member can handle 20 seats
  - Minimum 2 staff per hour
  - Maximum staff change between hours: 2 people
  - Variable demand: 40%-100% of capacity
  - Objective: Minimize labor cost ($25/hour per staff)
```

## Docker Usage

Can also run the MCP server directly from the GitHub Container Registry.

```bash
docker run -p 8081:8081 ghcr.io/sdiehl/usolver:latest
```

Then add the following to your client:

```json
{
  "mcpServers": {
    "sympy-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "-p",
        "8081:8081",
        "--rm",
        "ghcr.io/sdiehl/usolver:latest"
      ]
    }
  }
}
```

## License

Released under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
