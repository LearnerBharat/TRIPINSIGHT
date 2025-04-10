import os
import sys
import subprocess
import socket
import time

def check_port(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def run_server_check():
    """Check if the Django server can be started"""
    print("Checking if port 8000 is already in use...")
    if check_port(8000):
        print("Port 8000 is already in use. The server might already be running.")
        return
    
    print("Starting Django server for testing...")
    
    # Start the server in a separate process
    server_process = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "--noreload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait a bit for the server to start
    time.sleep(3)
    
    # Check if the server started successfully
    if server_process.poll() is not None:
        # Server process has terminated
        stdout, stderr = server_process.communicate()
        print("Server failed to start:")
        print(stderr)
        return
    
    print("Server started successfully!")
    
    # Try to access the admin page
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/admin/")
        if response.status_code == 200:
            print("Admin page is accessible!")
        else:
            print(f"Admin page returned status code: {response.status_code}")
    except Exception as e:
        print(f"Error accessing admin page: {e}")
    
    # Stop the server
    server_process.terminate()
    server_process.wait()
    print("Server stopped.")

if __name__ == "__main__":
    run_server_check()