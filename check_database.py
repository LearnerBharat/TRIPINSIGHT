import os
import django
import sqlite3

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.conf import settings

def check_database():
    """Check if the database file exists and is accessible"""
    db_path = settings.DATABASES['default']['NAME']
    
    print(f"Checking database at: {db_path}")
    
    if not os.path.exists(db_path):
        print("Database file does not exist!")
        return False
    
    try:
        # Try to connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if auth_user table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user'")
        if not cursor.fetchone():
            print("auth_user table does not exist! Migrations may not have been applied.")
            conn.close()
            return False
        
        # Check if django_admin_log table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_admin_log'")
        if not cursor.fetchone():
            print("django_admin_log table does not exist! Admin migrations may not have been applied.")
            conn.close()
            return False
        
        print("Database check passed successfully!")
        conn.close()
        return True
    except Exception as e:
        print(f"Error accessing database: {e}")
        return False

if __name__ == "__main__":
    check_database()