# Constrained Optimization Examples

This directory contains comprehensive examples demonstrating the capabilities of the Constrained Optimization MCP Server across various domains.

## 📊 **Quantitative Economics & Finance**

### Portfolio Optimization (`portfolio_optimization.py`)
- **Markowitz mean-variance optimization**
- **Black-Litterman model** with investor views
- **Risk parity optimization** for balanced risk allocation
- **ESG-constrained optimization** for sustainable investing
- **Efficient frontier analysis** and strategy comparison
- **Advanced risk metrics** and performance attribution

### Financial Examples (`constrained_opt_mcp/examples/financial/`)
- **Portfolio Optimization** (`portfolio_optimization.py`) - Advanced portfolio strategies
- **Risk Management** (`risk_management.py`) - VaR optimization and stress testing

## 🏭 **Scheduling & Operations**

### Job Shop Scheduling (`job_shop_scheduling.py`)
- **Multi-machine scheduling** with operation sequences
- **Makespan minimization** for production efficiency
- **Resource allocation** and timing constraints
- **Gantt chart visualization** of optimal schedules
- **Performance analysis** across different problem sizes

### Nurse Scheduling (`nurse_scheduling.py`)
- **Workforce scheduling** with complex constraints
- **Shift coverage requirements** and fairness considerations
- **Nurse preferences** and soft constraints
- **Weekend coverage** and consecutive shift limits
- **Schedule quality analysis** and visualization

## 🎯 **Combinatorial Optimization**

### N-Queens Problem (`nqueens.py`)
- **Constraint satisfaction** problem solving
- **Classic algorithmic challenge** with visualization
- **Performance analysis** across different board sizes
- **Solution visualization** on chessboard
- **Complexity analysis** and benchmarking

### Knapsack Problem (`knapsack.py`)
- **0/1 knapsack** and multiple knapsack variants
- **Binary decision variables** and integer programming
- **Value maximization** under weight constraints
- **Multiple knapsack** resource allocation
- **Performance analysis** and visualization

## 🏭 **Economic Production Planning**

### Economic Production Planning (`economic_production_planning.py`)
- **Multi-period production planning** with inventory management
- **Demand forecasting** and capacity constraints
- **Cost minimization** across production, holding, and shortage costs
- **Resource allocation** and supply chain optimization
- **Strategy comparison** (Just-in-Time vs Safety Stock vs Balanced)
- **Economic efficiency analysis** and performance metrics

## 🧮 **Mathematical Optimization**

### Interactive Demo (`constrained_optimization_demo.ipynb`)
- **Comprehensive Jupyter notebook** with all solver types
- **Interactive visualizations** and performance analysis
- **Mathematical theory** and formulations
- **Portfolio optimization** with advanced constraints
- **Real-time examples** and demonstrations

## 🚀 **Getting Started**

### Prerequisites
```bash
pip install constrained-opt-mcp
```

### Running Examples
```bash
# Run individual examples
python examples/nqueens.py
python examples/knapsack.py
python examples/job_shop_scheduling.py
python examples/nurse_scheduling.py
python examples/portfolio_optimization.py
python examples/economic_production_planning.py

# Run interactive notebook
jupyter notebook examples/constrained_optimization_demo.ipynb
```

### Example Structure
Each example follows a consistent structure:
1. **Problem Definition** - Clear description of the optimization problem
2. **Mathematical Formulation** - Complete mathematical model
3. **Implementation** - Code using the MCP server
4. **Visualization** - Charts and graphs for results
5. **Analysis** - Performance metrics and insights
6. **Comparison** - Different strategies or approaches

## 📈 **Key Features Demonstrated**

### Solver Integration
- **Z3** - Constraint satisfaction and logical reasoning
- **CVXPY** - Convex optimization and portfolio problems
- **HiGHS** - Linear programming and production planning
- **OR-Tools** - Constraint programming and scheduling

### Problem Types
- **Linear Programming** - Production planning, resource allocation
- **Convex Optimization** - Portfolio optimization, risk management
- **Constraint Satisfaction** - N-Queens, scheduling problems
- **Integer Programming** - Knapsack, assignment problems
- **Mixed-Integer Programming** - Complex scheduling and planning

### Visualization & Analysis
- **Interactive plots** and charts
- **Performance benchmarking** across problem sizes
- **Strategy comparison** and sensitivity analysis
- **Economic metrics** and efficiency analysis
- **Real-time optimization** results

## 🎯 **Use Cases**

### Financial Services
- Portfolio optimization and risk management
- Asset allocation and rebalancing
- ESG investing and sustainable finance
- Risk budgeting and factor investing

### Manufacturing & Operations
- Production planning and scheduling
- Resource allocation and capacity planning
- Supply chain optimization
- Inventory management

### Healthcare & Services
- Nurse and staff scheduling
- Resource allocation in hospitals
- Appointment scheduling
- Workforce optimization

### Research & Education
- Algorithm benchmarking and comparison
- Optimization theory demonstration
- Mathematical modeling examples
- Performance analysis and visualization

## 📚 **Documentation**

- **[API Reference](../docs/README.md)** - Complete API documentation
- **[PDF Guide](../docs/constrained_optimization_package.pdf)** - Comprehensive user guide
- **[Academic Paper](../docs/constrained_optimization_journal.pdf)** - Journal-style research paper
- **[Interactive Demo](constrained_optimization_demo.ipynb)** - Jupyter notebook with examples

## 🤝 **Contributing**

We welcome contributions! Please see the main README for guidelines on:
- Adding new examples
- Improving existing examples
- Adding new problem types
- Enhancing visualizations
- Performance optimization

## 📄 **License**

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.
