"""Install dependencies for DXT extension"""

import subprocess
import sys
import os

def install_requirements():
    """Install requirements to lib directory"""
    lib_dir = os.path.join(os.path.dirname(__file__), 'lib')
    
    # Install to lib directory
    subprocess.check_call([
        sys.executable, '-m', 'pip', 'install',
        '-r', 'requirements.txt',
        '--target', lib_dir
    ])
    
    print(f"Dependencies installed to {lib_dir}")

if __name__ == "__main__":
    install_requirements()