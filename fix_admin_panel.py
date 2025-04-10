import os
import sys
import subprocess
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from django.conf import settings
import sqlite3

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
        
        print("Database check passed successfully!")
        conn.close()
        return True
    except Exception as e:
        print(f"Error accessing database: {e}")
        return False

def check_superuser():
    """Check if any superusers exist and create one if needed"""
    superusers = User.objects.filter(is_superuser=True)

    if superusers.exists():
        print("Superusers found:")
        for user in superusers:
            print(f"Username: {user.username}, Email: {user.email}, Is active: {user.is_active}")
        return True
    else:
        print("No superusers found in the database.")
        
        # Create a superuser if none exists
        print("\nCreating a new superuser...")
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'
        
        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"Superuser created successfully with username: {username} and password: {password}")
            print("You can now log in to the admin panel with these credentials.")
            return True
        except Exception as e:
            print(f"Error creating superuser: {e}")
            return False

def apply_migrations():
    """Apply any pending migrations"""
    print("Applying migrations...")
    try:
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print("Migrations applied successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error applying migrations: {e}")
        return False

def check_jazzmin():
    """Check if jazzmin is installed correctly"""
    try:
        import jazzmin
        print("Jazzmin is installed correctly.")
        return True
    except ImportError:
        print("Jazzmin is not installed. Installing now...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "django-jazzmin"], check=True)
            print("Jazzmin installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing jazzmin: {e}")
            print("You can try to install it manually with: pip install django-jazzmin")
            return False

def fix_admin_panel():
    """Fix common issues with the admin panel"""
    print("Starting admin panel troubleshooting...\n")
    
    # Step 1: Check database
    if not check_database():
        print("\nDatabase issues detected. Attempting to apply migrations...")
        if not apply_migrations():
            print("\nFailed to fix database issues. You may need to recreate the database.")
            print("Try running: python manage.py flush")
            return False
    
    # Step 2: Check jazzmin
    if not check_jazzmin():
        print("\nJazzmin issues detected. You may need to remove it from INSTALLED_APPS in settings.py.")
        print("Edit project/settings.py and remove or comment out 'jazzmin' from INSTALLED_APPS.")
    
    # Step 3: Check superuser
    if not check_superuser():
        print("\nFailed to create a superuser. You may need to create one manually.")
        print("Try running: python manage.py createsuperuser")
        return False
    
    print("\nTroubleshooting complete!")
    print("Try accessing the admin panel at http://127.0.0.1:8000/admin/")
    print("If you still have issues, try restarting the server with: python manage.py runserver")
    
    return True

if __name__ == "__main__":
    fix_admin_panel()