import os
import sys
import subprocess

def run_script():
    """
    Run the add_maharashtra_places.py script to add Maharashtra tourist places to the database
    """
    print("Starting to add Maharashtra tourist places to the database...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the script
    script_path = os.path.join(current_dir, "add_maharashtra_places.py")
    
    # Run the script
    try:
        result = subprocess.run([sys.executable, script_path], 
                               capture_output=True, 
                               text=True, 
                               check=True)
        print(result.stdout)
        print("Maharashtra tourist places added successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error running the script: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    return True

if __name__ == "__main__":
    run_script()