import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User

# Check if any superusers exist
superusers = User.objects.filter(is_superuser=True)

if superusers.exists():
    print("Superusers found:")
    for user in superusers:
        print(f"Username: {user.username}, Email: {user.email}, Is active: {user.is_active}")
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
    except Exception as e:
        print(f"Error creating superuser: {e}")