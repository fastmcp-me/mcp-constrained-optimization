# Mathematical Reference for Constrained Optimization MCP Server

## Table of Contents

1. [Optimization Theory Fundamentals](#optimization-theory-fundamentals)
2. [Problem Classifications](#problem-classifications)
3. [Solver Mathematical Foundations](#solver-mathematical-foundations)
4. [Portfolio Optimization Mathematics](#portfolio-optimization-mathematics)
5. [Scheduling and Operations Research](#scheduling-and-operations-research)
6. [Combinatorial Optimization](#combinatorial-optimization)
7. [Economic Production Planning](#economic-production-planning)
8. [Complexity Analysis](#complexity-analysis)
9. [Solution Methods](#solution-methods)
10. [References](#references)

## Optimization Theory Fundamentals

### General Constrained Optimization Problem

The general form of a constrained optimization problem is:

$$\min_{x \in \mathbb{R}^n} f(x) \quad \text{subject to} \quad \begin{cases}
g_i(x) \leq 0, & i = 1, \ldots, m \\
h_j(x) = 0, & j = 1, \ldots, p \\
x \in \mathcal{X}
\end{cases}$$

Where:
- $f: \mathbb{R}^n \to \mathbb{R}$ is the **objective function**
- $g_i: \mathbb{R}^n \to \mathbb{R}$ are **inequality constraints**
- $h_j: \mathbb{R}^n \to \mathbb{R}$ are **equality constraints**
- $\mathcal{X} \subseteq \mathbb{R}^n$ is the **feasible region**

### Duality Theory

For any optimization problem, there exists a **dual problem**:

**Primal:** $\min_{x} f(x) \quad \text{s.t.} \quad g_i(x) \leq 0, \quad h_j(x) = 0$

**Dual:** $\max_{\lambda, \nu} \mathcal{L}(x^*, \lambda, \nu) \quad \text{s.t.} \quad \lambda \geq 0$

Where $\mathcal{L}(x, \lambda, \nu) = f(x) + \sum_i \lambda_i g_i(x) + \sum_j \nu_j h_j(x)$ is the **Lagrangian**.

### Optimality Conditions

#### Karush-Kuhn-Tucker (KKT) Conditions

For a solution $x^*$ to be optimal, there must exist multipliers $\lambda^* \geq 0$ and $\nu^*$ such that:

1. **Stationarity:** $\nabla f(x^*) + \sum_i \lambda_i^* \nabla g_i(x^*) + \sum_j \nu_j^* \nabla h_j(x^*) = 0$
2. **Primal feasibility:** $g_i(x^*) \leq 0, \quad h_j(x^*) = 0$
3. **Dual feasibility:** $\lambda_i^* \geq 0$
4. **Complementary slackness:** $\lambda_i^* g_i(x^*) = 0$

## Problem Classifications

### 1. Linear Programming (LP)

$$\min_{x} c^T x \quad \text{subject to} \quad Ax \leq b, \quad x \geq 0$$

**Properties:**
- Convex optimization problem
- Polynomial time solvable
- Simplex method, interior point methods

### 2. Quadratic Programming (QP)

$$\min_{x} \frac{1}{2}x^T Q x + c^T x \quad \text{subject to} \quad Ax \leq b, \quad x \geq 0$$

**Properties:**
- Convex if $Q \succeq 0$ (positive semidefinite)
- Interior point methods, active set methods

### 3. Convex Optimization

$$\min_{x} f(x) \quad \text{subject to} \quad g_i(x) \leq 0, \quad h_j(x) = 0$$

Where $f$ and $g_i$ are convex functions, and $h_j$ are affine functions.

**Properties:**
- Global optimum is unique
- Polynomial time solvable
- Duality gap is zero

### 4. Constraint Satisfaction Problems (CSP)

Find $x \in \mathcal{D}$ such that $C_1(x) \land C_2(x) \land \ldots \land C_k(x)$

Where $\mathcal{D}$ is the domain and $C_i$ are logical constraints.

**Properties:**
- NP-Complete in general
- Constraint propagation, backtracking
- Arc consistency, path consistency

## Solver Mathematical Foundations

### Z3 SMT Solver

**Satisfiability Modulo Theories (SMT)** extends Boolean satisfiability with theories:

- **Linear Arithmetic:** $x + 2y \leq 5$
- **Non-linear Arithmetic:** $x^2 + y^2 \leq 1$
- **Bit-vectors:** $x \& y = z$
- **Arrays:** $A[i] = v$
- **Uninterpreted Functions:** $f(x) = g(y)$

**Decision Procedures:**
- DPLL(T) algorithm
- Theory combination
- Model-based quantifier instantiation

### CVXPY Convex Optimization

**Disciplined Convex Programming (DCP)** rules:

1. **Atoms:** $x^2, |x|, \log(x), \exp(x)$
2. **Composition:** $f(g(x))$ where $f$ convex, $g$ affine
3. **Affine transformations:** $Ax + b$

**Canonicalization:**
- Problem transformed to standard form
- Conic programming formulation
- Interior point methods

### HiGHS Linear Programming

**Simplex Method:**
- Basic feasible solutions
- Pivot operations
- Bland's rule for cycling prevention

**Interior Point Methods:**
- Primal-dual path following
- Newton's method
- Barrier functions

### OR-Tools Constraint Programming

**Constraint Propagation:**
- Domain reduction
- Arc consistency (AC-3, AC-4)
- Path consistency

**Search Strategies:**
- Backtracking
- Branch and bound
- Local search

## Portfolio Optimization Mathematics

### Markowitz Mean-Variance Optimization

$$\max_{w} \mu^T w - \frac{\lambda}{2} w^T \Sigma w \quad \text{subject to} \quad \sum_{i=1}^{n} w_i = 1, \quad w_i \geq 0$$

Where:
- $w \in \mathbb{R}^n$: portfolio weights
- $\mu \in \mathbb{R}^n$: expected returns
- $\Sigma \in \mathbb{R}^{n \times n}$: covariance matrix
- $\lambda \geq 0$: risk aversion parameter

### Black-Litterman Model

**Expected Returns:**
$$\Pi = \lambda \Sigma w_{market}$$

**Posterior Returns:**
$$\mu_{BL} = [(\tau \Sigma)^{-1} + P^T \Omega^{-1} P]^{-1} [(\tau \Sigma)^{-1} \Pi + P^T \Omega^{-1} Q]$$

Where:
- $\Pi$: market implied returns
- $P$: pick matrix for views
- $Q$: view returns
- $\Omega$: uncertainty matrix
- $\tau$: scaling factor

### Risk Parity Optimization

$$\min_{w} \sum_{i=1}^{n} \sum_{j=1}^{n} (w_i \frac{\partial \sigma_p}{\partial w_i} - w_j \frac{\partial \sigma_p}{\partial w_j})^2$$

Where $\sigma_p = \sqrt{w^T \Sigma w}$ is portfolio volatility.

### ESG-Constrained Optimization

$$\max_{w} \mu^T w - \frac{\lambda}{2} w^T \Sigma w \quad \text{subject to} \quad \begin{cases}
\sum_{i=1}^{n} w_i = 1 \\
w_i \geq 0 \\
\sum_{i=1}^{n} w_i \cdot ESG_i \geq \theta
\end{cases}$$

Where $ESG_i$ is the ESG score of asset $i$ and $\theta$ is the minimum ESG threshold.

## Scheduling and Operations Research

### Job Shop Scheduling

**Variables:**
- $s_{ij} \geq 0$: start time of operation $j$ of job $i$
- $C_{max}$: makespan

**Objective:**
$$\min C_{max}$$

**Constraints:**
1. **Precedence:** $s_{ij} + p_{ij} \leq s_{i,j+1}$
2. **Resource capacity:** $s_{ij} + p_{ij} \leq s_{kl}$ or $s_{kl} + p_{kl} \leq s_{ij}$ for same machine
3. **Makespan:** $s_{ij} + p_{ij} \leq C_{max}$

### Nurse Scheduling

**Variables:**
- $x_{n,s,d} \in \{0,1\}$: nurse $n$ works shift $s$ on day $d$
- $y_{n,d} \in \{0,1\}$: nurse $n$ works on day $d$

**Objective:**
$$\min \sum_{n,s,d} c_{n,s} x_{n,s,d} + \sum_{n,d} p_n y_{n,d}$$

**Constraints:**
1. **Coverage:** $\sum_n x_{n,s,d} \geq R_{s,d}$
2. **One shift per day:** $\sum_s x_{n,s,d} \leq 1$
3. **Consecutive days limit:** $\sum_{d=k}^{k+L} y_{n,d} \leq L_{max}$

## Combinatorial Optimization

### N-Queens Problem

**Variables:** $x_{i,j} \in \{0,1\}$ (queen at position $(i,j)$)

**Constraints:**
1. **Row:** $\sum_{j=1}^{n} x_{i,j} = 1 \quad \forall i$
2. **Column:** $\sum_{i=1}^{n} x_{i,j} = 1 \quad \forall j$
3. **Diagonal:** $\sum_{i-j=k} x_{i,j} \leq 1 \quad \forall k$
4. **Anti-diagonal:** $\sum_{i+j=k} x_{i,j} \leq 1 \quad \forall k$

### Knapsack Problem

**0/1 Knapsack:**
$$\max \sum_{i=1}^{n} v_i x_i \quad \text{subject to} \quad \sum_{i=1}^{n} w_i x_i \leq W, \quad x_i \in \{0,1\}$$

**Multiple Knapsack:**
$$\max \sum_{i=1}^{n} \sum_{j=1}^{m} v_i x_{ij} \quad \text{subject to} \quad \begin{cases}
\sum_{j=1}^{m} x_{ij} \leq 1 \quad \forall i \\
\sum_{i=1}^{n} w_i x_{ij} \leq W_j \quad \forall j \\
x_{ij} \in \{0,1\}
\end{cases}$$

## Economic Production Planning

### Multi-Period Production Planning

**Variables:**
- $x_{it} \geq 0$: production quantity of product $i$ in period $t$
- $I_{it} \geq 0$: inventory level of product $i$ at end of period $t$
- $y_{it} \in \{0,1\}$: setup indicator for product $i$ in period $t$

**Objective:**
$$\min \sum_{i \in I} \sum_{t=1}^{T} (p_i x_{it} + h_i I_{it} + s_i y_{it})$$

**Constraints:**
1. **Inventory balance:** $I_{i,t-1} + x_{it} - I_{it} = D_{it}$
2. **Resource capacity:** $\sum_{i \in I} c_{ir} x_{it} \leq K_{rt}$
3. **Setup:** $x_{it} \leq M y_{it}$

### Capacitated Lot Sizing Problem (CLSP)

**Single product, multiple periods:**
$$\min \sum_{t=1}^{T} (p_t x_t + h_t I_t + s_t y_t)$$

**Subject to:**
- $I_{t-1} + x_t - I_t = D_t$
- $x_t \leq M y_t$
- $x_t, I_t \geq 0, \quad y_t \in \{0,1\}$

## Complexity Analysis

### Problem Complexity Classes

| Problem Type | Complexity | Solver | Notes |
|--------------|------------|--------|-------|
| Linear Programming | P | HiGHS | Simplex, Interior Point |
| Convex Optimization | P | CVXPY | Interior Point |
| Constraint Satisfaction | NP-Complete | Z3 | SMT Solving |
| Job Shop Scheduling | NP-Hard | OR-Tools | Heuristics |
| Knapsack (0/1) | NP-Complete | OR-Tools | Dynamic Programming |
| N-Queens | NP-Complete | OR-Tools | Backtracking |
| Portfolio Optimization | P | CVXPY | Quadratic Programming |

### Approximation Algorithms

**Performance Ratio:** $\frac{OPT}{ALG} \leq \rho$ where $ALG$ is algorithm solution and $OPT$ is optimal solution.

**Examples:**
- Knapsack greedy: $\rho = 2$
- Job shop scheduling: Various heuristics
- Portfolio optimization: Exact for convex case

## Solution Methods

### Exact Methods

1. **Branch and Bound**
   - Divide problem into subproblems
   - Prune suboptimal branches
   - Maintain best solution found

2. **Cutting Plane Methods**
   - Add valid inequalities
   - Strengthen LP relaxation
   - Gomory cuts, Chvátal-Gomory cuts

3. **Dynamic Programming**
   - Optimal substructure
   - Overlapping subproblems
   - Memoization

### Heuristic Methods

1. **Genetic Algorithms**
   - Population-based search
   - Crossover and mutation
   - Fitness evaluation

2. **Simulated Annealing**
   - Probabilistic acceptance
   - Temperature schedule
   - Local search

3. **Tabu Search**
   - Memory-based search
   - Tabu list
   - Aspiration criteria

### Decomposition Methods

1. **Dantzig-Wolfe Decomposition**
   - Master problem + subproblems
   - Column generation
   - Pricing problem

2. **Benders Decomposition**
   - Master problem + subproblem
   - Cut generation
   - Feasibility cuts

## References

1. Boyd, S., & Vandenberghe, L. (2004). *Convex Optimization*. Cambridge University Press.

2. Nocedal, J., & Wright, S. J. (2006). *Numerical Optimization*. Springer.

3. Markowitz, H. (1952). Portfolio Selection. *Journal of Finance*, 7(1), 77-91.

4. Black, F., & Litterman, R. (1992). Global Portfolio Optimization. *Financial Analysts Journal*, 48(5), 28-43.

5. Pinedo, M. (2016). *Scheduling: Theory, Algorithms, and Systems*. Springer.

6. Lawler, E. L. (1976). *Combinatorial Optimization: Networks and Matroids*. Holt, Rinehart and Winston.

7. Silver, E. A., Pyke, D. F., & Peterson, R. (1998). *Inventory and Production Management in Supply Chains*. Wiley.

8. de Moura, L., & Bjørner, N. (2011). Satisfiability Modulo Theories: Introduction and Applications. *Communications of the ACM*, 54(7), 69-77.

9. Diamond, S., & Boyd, S. (2016). CVXPY: A Python-embedded modeling language for convex optimization. *Journal of Machine Learning Research*, 17(83), 1-5.

10. Huangfu, Q., & Hall, J. A. J. (2018). Parallelizing the dual revised simplex method. *Mathematical Programming Computation*, 10(1), 119-142.
