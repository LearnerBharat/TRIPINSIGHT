#!/usr/bin/env python
"""
Script to install required dependencies for TripInsight.
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies from requirements.txt."""
    print("\n=== Installing TripInsight Dependencies ===\n")
    
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(script_dir, 'requirements.txt')
    
    # Check if requirements.txt exists
    if not os.path.exists(requirements_path):
        print(f"Error: requirements.txt not found at {requirements_path}")
        return False
    
    try:
        # Install dependencies
        print(f"Installing dependencies from {requirements_path}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_path])
        
        # Explicitly install python-dotenv to ensure it's available
        print("Ensuring python-dotenv is installed...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-dotenv>=0.19.0'])
        
        print("\n✅ Dependencies installed successfully!")
        
        # Prompt to set up Google Maps API key
        setup_api = input("\nWould you like to set up your Google Maps API key now? (y/n): ").strip().lower()
        if setup_api == 'y':
            setup_script = os.path.join(script_dir, 'setup_api_key.py')
            subprocess.check_call([sys.executable, setup_script])
        else:
            print("\nYou can set up your Google Maps API key later by running:")
            print("python setup_api_key.py")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError installing dependencies: {e}")
        return False

if __name__ == "__main__":
    install_dependencies()