import os
import sys
import django
import sqlite3

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.conf import settings

def reset_database():
    """Reset the database by deleting it and recreating it"""
    db_path = settings.DATABASES['default']['NAME']
    
    # Check if the database file exists
    if os.path.exists(db_path):
        print(f"Removing existing database at {db_path}")
        os.remove(db_path)
    
    # Create a new empty database
    conn = sqlite3.connect(db_path)
    conn.close()
    print(f"Created new empty database at {db_path}")
    
    # Apply migrations
    print("Now run 'python manage.py migrate' to apply all migrations")

if __name__ == "__main__":
    # Ask for confirmation
    confirm = input("This will delete your database and all data. Are you sure? (y/n): ")
    if confirm.lower() == 'y':
        reset_database()
    else:
        print("Operation cancelled.")