#!/usr/bin/env python
"""
Setup script for configuring the Google Maps API key in TripInsight.
This script updates the .env file with the provided API key.
"""

import os
import sys
from pathlib import Path

def setup_api_key():
    """Set up the Google Maps API key in the .env file."""
    print("\n=== TripInsight Google Maps API Key Setup ===\n")
    
    # Check if .env file exists
    env_path = Path('.env')
    
    if not env_path.exists():
        print("Creating new .env file...")
        with open(env_path, 'w') as f:
            f.write("# Environment Variables for TripInsight\n")
    
    # Get API key from user
    api_key = input("Enter your Google Maps API key: ").strip()
    
    if not api_key:
        print("Error: API key cannot be empty.")
        return False
    
    # Read existing .env file
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Check if GOOGLE_MAPS_API_KEY already exists
    key_exists = False
    new_lines = []
    
    for line in lines:
        if line.startswith('GOOGLE_MAPS_API_KEY='):
            new_lines.append(f'GOOGLE_MAPS_API_KEY={api_key}\n')
            key_exists = True
        else:
            new_lines.append(line)
    
    # If key doesn't exist, add it
    if not key_exists:
        new_lines.append(f'GOOGLE_MAPS_API_KEY={api_key}\n')
    
    # Write updated content back to .env file
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    print("\n✅ Google Maps API key has been successfully configured!")
    print("\nTo obtain a Google Maps API key:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the following APIs:")
    print("   - Maps JavaScript API")
    print("   - Geocoding API")
    print("   - Distance Matrix API")
    print("4. Create credentials to get your API key")
    print("\nRestart your Django server for the changes to take effect.")
    
    return True

if __name__ == "__main__":
    setup_api_key()