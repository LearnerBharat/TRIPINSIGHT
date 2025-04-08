import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Import Django migration executor
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

def apply_migrations():
    """Apply all pending migrations"""
    executor = MigrationExecutor(connection)
    
    # Get the migration plan
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    
    if plan:
        print(f"Applying {len(plan)} pending migrations:")
        for migration, backwards in plan:
            print(f" - {migration}")
        
        # Apply migrations
        executor.migrate(executor.loader.graph.leaf_nodes())
        print("Migrations applied successfully!")
    else:
        print("No pending migrations to apply.")

if __name__ == "__main__":
    apply_migrations()