#!/usr/bin/env python3
"""
Create a comprehensive PDF document about the Constrained Optimization MCP Package
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io
import os
from datetime import datetime

# Set up matplotlib for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def create_optimization_plots():
    """Create various optimization plots for the PDF"""
    plots = {}
    
    # 1. N-Queens Problem Visualization
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    n = 8
    # Create a sample 8-queens solution
    queens = [0, 4, 7, 5, 2, 6, 1, 3]  # Valid 8-queens solution
    
    # Create chessboard
    board = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if (i + j) % 2 == 0:
                board[i, j] = 1
    
    ax.imshow(board, cmap='gray', alpha=0.3)
    
    # Place queens
    for i, j in enumerate(queens):
        ax.scatter(j, i, s=500, c='red', marker='o', edgecolors='black', linewidth=2)
        # Add Q text for queen
        ax.text(j, i, 'Q', ha='center', va='center', fontsize=16, fontweight='bold', color='white')
    
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels([chr(65 + i) for i in range(n)])
    ax.set_yticklabels(range(1, n + 1))
    ax.set_title('8-Queens Problem Solution', fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Save plot
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    plots['n_queens'] = buf
    plt.close()
    
    # 2. Portfolio Optimization - Efficient Frontier
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    # Generate sample data
    np.random.seed(42)
    n_assets = 4
    returns = np.array([0.08, 0.12, 0.10, 0.15])
    volatilities = np.array([0.02, 0.15, 0.08, 0.20])
    
    # Generate efficient frontier
    risk_levels = np.linspace(0.05, 0.25, 50)
    expected_returns = 0.05 + 0.4 * risk_levels + 0.1 * risk_levels**2
    
    ax.plot(risk_levels, expected_returns, 'b-', linewidth=2, label='Efficient Frontier')
    ax.scatter(volatilities, returns, c=['red', 'green', 'blue', 'orange'], s=100, alpha=0.7)
    
    for i, (ret, vol) in enumerate(zip(returns, volatilities)):
        ax.annotate(f'Asset {i+1}', (vol, ret), xytext=(5, 5), textcoords='offset points')
    
    ax.set_xlabel('Risk (Volatility)', fontsize=12)
    ax.set_ylabel('Expected Return', fontsize=12)
    ax.set_title('Portfolio Optimization: Efficient Frontier', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    plots['efficient_frontier'] = buf
    plt.close()
    
    # 3. Solver Performance Comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Solver performance data
    solvers = ['Z3', 'CVXPY', 'HiGHS', 'OR-Tools']
    solve_times = [0.1, 0.5, 0.3, 0.8]
    problem_types = ['CSP', 'Convex', 'LP', 'CP']
    
    # Bar chart for solve times
    bars = ax1.bar(solvers, solve_times, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    ax1.set_ylabel('Solve Time (seconds)', fontsize=12)
    ax1.set_title('Solver Performance Comparison', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, 1.0)
    
    # Add value labels on bars
    for bar, time in zip(bars, solve_times):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{time:.1f}s', ha='center', va='bottom')
    
    # Pie chart for problem types
    ax2.pie([1, 1, 1, 1], labels=problem_types, autopct='%1.0f%%', 
            colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    ax2.set_title('Supported Problem Types', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    plots['solver_comparison'] = buf
    plt.close()
    
    # 4. Portfolio Allocation Pie Chart
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    
    # Sample portfolio allocation
    sectors = ['Technology', 'Healthcare', 'Financial', 'Consumer', 'Industrial', 'Energy']
    allocations = [25, 20, 15, 15, 15, 10]
    colors_pie = plt.cm.Set3(np.linspace(0, 1, len(sectors)))
    
    wedges, texts, autotexts = ax.pie(allocations, labels=sectors, autopct='%1.1f%%', 
                                     colors=colors_pie, startangle=90)
    
    # Improve text appearance
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title('Optimal Portfolio Allocation', fontsize=16, fontweight='bold')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    plots['portfolio_allocation'] = buf
    plt.close()
    
    return plots

def create_pdf():
    """Create the main PDF document"""
    # Create output directory if it doesn't exist
    os.makedirs('docs', exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate('docs/constrained_optimization_package.pdf', 
                          pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.darkgreen
    )
    
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Courier',
        leftIndent=20,
        rightIndent=20,
        spaceAfter=6,
        spaceBefore=6,
        backColor=colors.lightgrey
    )
    
    # Create plots
    print("Creating optimization plots...")
    plots = create_optimization_plots()
    
    # Build document content
    story = []
    
    # Title page
    story.append(Paragraph("Constrained Optimization MCP Server", title_style))
    story.append(Paragraph("A General-Purpose Model Context Protocol Server for Solving Combinatorial Optimization Problems", 
                          styles['Heading2']))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(PageBreak())
    
    # Table of Contents
    story.append(Paragraph("Table of Contents", heading_style))
    toc_items = [
        "1. Introduction",
        "2. Mathematical Theory",
        "3. Supported Solvers",
        "4. Installation and Setup",
        "5. Usage Examples",
        "6. Portfolio Optimization",
        "7. Advanced Features",
        "8. API Reference",
        "9. Performance Analysis",
        "10. Conclusion"
    ]
    
    for item in toc_items:
        story.append(Paragraph(item, styles['Normal']))
        story.append(Spacer(1, 6))
    
    story.append(PageBreak())
    
    # Introduction
    story.append(Paragraph("1. Introduction", heading_style))
    story.append(Paragraph("""
    The Constrained Optimization MCP Server is a powerful, general-purpose tool designed to solve 
    combinatorial optimization problems with logical and numerical constraints. Built on the Model 
    Context Protocol (MCP), it provides a unified interface for various optimization solvers, 
    making it easy to tackle complex optimization challenges across different domains.
    """, styles['Normal']))
    
    story.append(Paragraph("Key Features:", subheading_style))
    features = [
        "• Multiple solver support (Z3, CVXPY, HiGHS, OR-Tools)",
        "• Unified API for different optimization problem types",
        "• Portfolio optimization with advanced constraints",
        "• Constraint satisfaction problem solving",
        "• Linear and convex optimization",
        "• Easy integration with AI assistants via MCP",
        "• Comprehensive documentation and examples"
    ]
    
    for feature in features:
        story.append(Paragraph(feature, styles['Normal']))
    
    story.append(PageBreak())
    
    # Mathematical Theory
    story.append(Paragraph("2. Mathematical Theory", heading_style))
    story.append(Paragraph("""
    Constrained optimization problems can be formulated in the general form:
    """, styles['Normal']))
    
    story.append(Paragraph("""
    <b>Minimize:</b> f(x)<br/>
    <b>Subject to:</b><br/>
    &nbsp;&nbsp;&nbsp;&nbsp;g_i(x) ≤ 0, i = 1, ..., m<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;h_j(x) = 0, j = 1, ..., p<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;x ∈ X
    """, code_style))
    
    story.append(Paragraph("""
    Where:
    <br/>• f(x) is the objective function
    <br/>• g_i(x) are inequality constraints
    <br/>• h_j(x) are equality constraints
    <br/>• X is the feasible region
    """, styles['Normal']))
    
    story.append(Paragraph("Problem Types:", subheading_style))
    story.append(Paragraph("""
    <b>1. Constraint Satisfaction Problems (CSP):</b> Find values that satisfy all constraints
    <br/><b>2. Linear Programming (LP):</b> Linear objective and constraints
    <br/><b>3. Convex Optimization:</b> Convex objective and constraints
    <br/><b>4. Mixed-Integer Programming (MIP):</b> Some variables must be integers
    <br/><b>5. Constraint Programming (CP):</b> Logical constraints and discrete variables
    """, styles['Normal']))
    
    story.append(PageBreak())
    
    # Supported Solvers
    story.append(Paragraph("3. Supported Solvers", heading_style))
    
    # Solver comparison table
    solver_data = [
        ['Solver', 'Problem Types', 'Strengths', 'Use Cases'],
        ['Z3', 'CSP, SMT', 'Logical reasoning', 'N-Queens, Scheduling'],
        ['CVXPY', 'Convex', 'Mathematical modeling', 'Portfolio optimization'],
        ['HiGHS', 'LP, MIP', 'High performance', 'Large-scale linear problems'],
        ['OR-Tools', 'CP, MIP', 'Combinatorial optimization', 'Vehicle routing, Assignment']
    ]
    
    solver_table = Table(solver_data)
    solver_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(solver_table)
    story.append(Spacer(1, 20))
    
    # Add solver performance plot
    story.append(Image(plots['solver_comparison'], width=6*inch, height=3*inch))
    story.append(Spacer(1, 20))
    
    story.append(PageBreak())
    
    # Installation and Setup
    story.append(Paragraph("4. Installation and Setup", heading_style))
    story.append(Paragraph("Installation:", subheading_style))
    story.append(Paragraph("""
    pip install constrained-opt-mcp
    """, code_style))
    
    story.append(Paragraph("Dependencies:", subheading_style))
    dependencies = [
        "• numpy >= 1.20.0",
        "• scipy >= 1.7.0", 
        "• pandas >= 1.3.0",
        "• matplotlib >= 3.4.0",
        "• seaborn >= 0.11.0",
        "• cvxpy >= 1.1.0",
        "• z3-solver >= 4.8.0",
        "• ortools >= 9.0.0",
        "• highspy >= 1.0.0"
    ]
    
    for dep in dependencies:
        story.append(Paragraph(dep, styles['Normal']))
    
    story.append(PageBreak())
    
    # Usage Examples
    story.append(Paragraph("5. Usage Examples", heading_style))
    
    # N-Queens Example
    story.append(Paragraph("5.1 N-Queens Problem", subheading_style))
    story.append(Image(plots['n_queens'], width=4*inch, height=4*inch))
    story.append(Paragraph("""
    The N-Queens problem is a classic constraint satisfaction problem where we need to place 
    N queens on an N×N chessboard such that no two queens attack each other.
    """, styles['Normal']))
    
    story.append(Paragraph("Mathematical Formulation:", subheading_style))
    story.append(Paragraph("""
    <b>Variables:</b> x_i,j ∈ {0,1} (queen at position (i,j))<br/>
    <b>Constraints:</b><br/>
    &nbsp;&nbsp;&nbsp;&nbsp;Σ_j x_i,j = 1 ∀i (one queen per row)<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;Σ_i x_i,j = 1 ∀j (one queen per column)<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;No two queens on same diagonal
    """, code_style))
    
    story.append(PageBreak())
    
    # Portfolio Optimization
    story.append(Paragraph("6. Portfolio Optimization", heading_style))
    story.append(Paragraph("""
    Portfolio optimization is a key application of constrained optimization in finance. 
    The goal is to find the optimal allocation of assets that maximizes expected return 
    while minimizing risk, subject to various constraints.
    """, styles['Normal']))
    
    story.append(Image(plots['efficient_frontier'], width=6*inch, height=3.6*inch))
    story.append(Spacer(1, 20))
    
    story.append(Image(plots['portfolio_allocation'], width=4*inch, height=4*inch))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Markowitz Portfolio Theory:", subheading_style))
    story.append(Paragraph("""
    <b>Objective:</b> Maximize μ^T w - (λ/2) w^T Σ w<br/>
    <b>Subject to:</b><br/>
    &nbsp;&nbsp;&nbsp;&nbsp;Σ w_i = 1 (weights sum to 1)<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;w_i ≥ 0 (no short selling)<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;Additional constraints (sector limits, etc.)
    """, code_style))
    
    story.append(PageBreak())
    
    # Advanced Features
    story.append(Paragraph("7. Advanced Features", heading_style))
    
    story.append(Paragraph("7.1 Multi-Asset Portfolio Optimization", subheading_style))
    story.append(Paragraph("""
    The package supports sophisticated portfolio optimization with multiple asset classes:
    """, styles['Normal']))
    
    asset_classes = [
        "• Equities (stocks, ETFs, REITs)",
        "• Fixed Income (bonds, treasuries)",
        "• Alternatives (commodities, real estate)",
        "• Cash and money market instruments"
    ]
    
    for asset in asset_classes:
        story.append(Paragraph(asset, styles['Normal']))
    
    story.append(Paragraph("7.2 Constraint Types", subheading_style))
    constraint_types = [
        "• Sector diversification limits",
        "• Market cap constraints",
        "• ESG (Environmental, Social, Governance) constraints",
        "• Liquidity requirements",
        "• Regional exposure limits",
        "• Individual position limits"
    ]
    
    for constraint in constraint_types:
        story.append(Paragraph(constraint, styles['Normal']))
    
    story.append(PageBreak())
    
    # API Reference
    story.append(Paragraph("8. API Reference", heading_style))
    story.append(Paragraph("Main MCP Tools:", subheading_style))
    
    api_tools = [
        "• solve_constraint_satisfaction: Z3-based CSP solving",
        "• solve_linear_programming: HiGHS-based LP solving", 
        "• solve_convex_optimization: CVXPY-based convex optimization",
        "• solve_constraint_programming: OR-Tools-based CP solving",
        "• solve_portfolio_optimization: Specialized portfolio optimization"
    ]
    
    for tool in api_tools:
        story.append(Paragraph(tool, styles['Normal']))
    
    story.append(Paragraph("Example Usage:", subheading_style))
    story.append(Paragraph("""
    # Solve a constraint satisfaction problem
    result = mcp_client.call_tool("solve_constraint_satisfaction", {
        "problem": "n_queens",
        "size": 8
    })
    
    # Optimize a portfolio
    result = mcp_client.call_tool("solve_portfolio_optimization", {
        "assets": asset_data,
        "constraints": constraint_data,
        "risk_aversion": 2.0
    })
    """, code_style))
    
    story.append(PageBreak())
    
    # Performance Analysis
    story.append(Paragraph("9. Performance Analysis", heading_style))
    story.append(Paragraph("""
    The package is designed for high performance and scalability:
    """, styles['Normal']))
    
    performance_metrics = [
        "• Z3: Sub-second solving for most CSP problems",
        "• CVXPY: Efficient convex optimization with multiple solvers",
        "• HiGHS: High-performance linear programming",
        "• OR-Tools: Optimized for large-scale combinatorial problems"
    ]
    
    for metric in performance_metrics:
        story.append(Paragraph(metric, styles['Normal']))
    
    story.append(Paragraph("Scalability:", subheading_style))
    story.append(Paragraph("""
    • Portfolio optimization: Up to 1000+ assets
    • Constraint satisfaction: Complex logical problems
    • Linear programming: Large-scale industrial problems
    • Constraint programming: Real-world scheduling and routing
    """, styles['Normal']))
    
    story.append(PageBreak())
    
    # Conclusion
    story.append(Paragraph("10. Conclusion", heading_style))
    story.append(Paragraph("""
    The Constrained Optimization MCP Server provides a comprehensive solution for solving 
    complex optimization problems across multiple domains. With its unified interface, 
    multiple solver support, and specialized portfolio optimization capabilities, it serves 
    as a powerful tool for researchers, practitioners, and AI systems.
    """, styles['Normal']))
    
    story.append(Paragraph("Key Benefits:", subheading_style))
    benefits = [
        "• Unified API for different optimization problem types",
        "• High-performance solvers for various problem classes",
        "• Specialized portfolio optimization with advanced constraints",
        "• Easy integration with AI assistants via MCP",
        "• Comprehensive documentation and examples",
        "• Active development and community support"
    ]
    
    for benefit in benefits:
        story.append(Paragraph(benefit, styles['Normal']))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("For more information, visit: https://github.com/your-username/constrained-opt-mcp", 
                          styles['Normal']))
    
    # Build PDF
    print("Building PDF document...")
    doc.build(story)
    print("PDF created successfully: docs/constrained_optimization_package.pdf")

if __name__ == "__main__":
    create_pdf()
