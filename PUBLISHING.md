# Publishing Guide for Constrained Optimization MCP Server

## Overview

This guide explains how to publish the **General Purpose MCP Server for Constrained Optimization** to PyPI for use by AI agents in optimization tasks such as portfolio optimization, scheduling, and combinatorial problems.

## Package Information

- **Name**: `constrained-opt-mcp`
- **Description**: General Purpose MCP Server for Constrained Optimization - AI agents for optimization tasks such as portfolio optimization, scheduling, and combinatorial problems
- **PyPI URL**: https://pypi.org/project/constrained-opt-mcp/
- **GitHub Repository**: [Your Repository URL]

## Prerequisites

1. **Python 3.10+** installed
2. **Git** configured with your credentials
3. **PyPI account** with API token
4. **GitHub repository** with proper permissions

## Publishing Methods

### Method 1: Automated GitHub Actions (Recommended)

The package is configured with GitHub Actions for automated publishing:

1. **Create a Release**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Go to GitHub Releases**:
   - Navigate to your repository
   - Click "Releases" → "Create a new release"
   - Select tag `v1.0.0`
   - Add release notes
   - Click "Publish release"

3. **GitHub Actions will automatically**:
   - Build the package for Python 3.10, 3.11, 3.12
   - Test the distributions
   - Publish to PyPI

### Method 2: Manual Publishing

1. **Install build tools**:
   ```bash
   pip install build twine
   ```

2. **Build the package**:
   ```bash
   python -m build
   ```

3. **Test the package**:
   ```bash
   twine check dist/*
   pip install dist/*.whl --force-reinstall
   ```

4. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

### Method 3: Using the Build Script

Run the automated build and test script:

```bash
python scripts/build_and_test.py
```

## Package Features

### 🎯 **Optimization Capabilities**
- **Constraint Satisfaction Problems** (Z3 SMT solver)
- **Convex Optimization** (CVXPY)
- **Linear Programming** (HiGHS)
- **Constraint Programming** (OR-Tools)

### 🤖 **AI Agent Integration**
- **Model Context Protocol (MCP)** server
- **Unified API** for different optimization types
- **Real-time optimization** for AI agents
- **Portfolio optimization** with advanced constraints
- **Scheduling and operations** research

### 📊 **Use Cases**
- **Portfolio Optimization**: Markowitz, Black-Litterman, Risk Parity, ESG-constrained
- **Scheduling**: Job shop scheduling, nurse scheduling, resource allocation
- **Combinatorial Problems**: N-Queens, knapsack, assignment problems
- **Economic Planning**: Multi-period production planning, inventory management

## Installation

Once published, users can install the package:

```bash
pip install constrained-opt-mcp
```

## Usage Example

```python
from constrained_opt_mcp.models.ortools_models import (
    ORToolsProblem, ORToolsVariable, ORToolsConstraint
)
from constrained_opt_mcp.solvers.ortools_solver import solve_problem

# Create optimization problem
problem = ORToolsProblem(
    name="Portfolio Optimization",
    problem_type="constraint_programming"
)

# Add variables and constraints
# ... (see examples/)

# Solve the problem
solution = solve_problem(problem)
```

## Version Management

### Semantic Versioning

- **MAJOR.MINOR.PATCH** (e.g., 1.0.0)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Version Bump Process

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with changes
3. **Create git tag**: `git tag v1.0.1`
4. **Push tag**: `git push origin v1.0.1`
5. **Create GitHub release**

## Quality Assurance

### Pre-Publication Checklist

- [ ] All tests pass
- [ ] Documentation is complete
- [ ] Examples work correctly
- [ ] Package builds without errors
- [ ] Version number updated
- [ ] CHANGELOG.md updated
- [ ] README.md is current

### Testing

```bash
# Run all tests
python -m pytest tests/

# Test package installation
pip install dist/*.whl --force-reinstall

# Test imports
python -c "import constrained_opt_mcp"
```

## Troubleshooting

### Common Issues

1. **Build fails**: Check Python version compatibility
2. **Upload fails**: Verify PyPI credentials
3. **Import errors**: Check package structure
4. **Version conflicts**: Update dependencies

### Support

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory

## Security

- **API tokens** are stored as GitHub secrets
- **Trusted publishing** is enabled for PyPI
- **Environment protection** rules are configured
- **Dependency scanning** is enabled

## Monitoring

After publication, monitor:

- **PyPI download statistics**
- **GitHub repository stars/forks**
- **Issue reports and bug reports**
- **User feedback and contributions**

## Next Steps

1. **Publish initial version** (1.0.0)
2. **Monitor usage** and feedback
3. **Iterate** based on user needs
4. **Add new features** and examples
5. **Maintain** and update regularly

---

**Happy Publishing! 🚀**

The General Purpose MCP Server for Constrained Optimization is ready to help AI agents solve complex optimization problems across multiple domains.
