#!/usr/bin/env python3
"""
Build and test script for constrained-opt-mcp package
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main build and test process"""
    print("🚀 Building and testing constrained-opt-mcp package")
    print("=" * 60)
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    if os.path.exists("dist"):
        import shutil
        shutil.rmtree("dist")
    if os.path.exists("build"):
        import shutil
        shutil.rmtree("build")
    if os.path.exists("*.egg-info"):
        import glob
        for egg_info in glob.glob("*.egg-info"):
            shutil.rmtree(egg_info)
    
    # Install build dependencies
    if not run_command("python -m pip install build twine", "Installing build dependencies"):
        return False
    
    # Build package
    if not run_command("python -m build", "Building package"):
        return False
    
    # Check distributions
    if not run_command("twine check dist/*", "Checking distributions"):
        return False
    
    # Test installation
    print("\n🧪 Testing package installation...")
    test_commands = [
        "python -m pip install dist/*.whl --force-reinstall",
        "python -c \"import constrained_opt_mcp; print('✅ Package imported successfully')\"",
        "python -c \"from constrained_opt_mcp.models import ortools_models; print('✅ Models imported successfully')\"",
        "python -c \"from constrained_opt_mcp.solvers import ortools_solver; print('✅ Solvers imported successfully')\"",
        "python -c \"from constrained_opt_mcp.server import main; print('✅ Server module imported successfully')\"",
    ]
    
    for cmd in test_commands:
        if not run_command(cmd, f"Testing: {cmd}"):
            return False
    
    print("\n🎉 Package build and test completed successfully!")
    print("📦 Package files created in dist/")
    print("🚀 Ready for PyPI publication!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
