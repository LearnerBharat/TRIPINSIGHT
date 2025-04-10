import os
import re
from pathlib import Path

def fix_distance_references(directory):
    """
    Fix distance references in template files by replacing specific distance values
    with generic 'Nearby attraction' text
    """
    # Define the patterns to look for
    patterns = [
        r'<i class="fas fa-route"></i>\s*\{\{\s*forloop\.counter\|add:\d+\s*\}\}\s*km away',
        r'<i class="fas fa-route"></i>\s*\d+\s*km away',
        r'<span>\s*\d+\s*km away\s*</span>',
        r'<div class="distance">\s*\d+\s*km away\s*</div>'
    ]
    
    # Define the replacement text
    replacement = '<i class="fas fa-route"></i> Nearby attraction'
    
    # Get all HTML files in the directory and subdirectories
    template_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                template_files.append(os.path.join(root, file))
    
    # Process each file
    for file_path in template_files:
        print(f"Processing {file_path}...")
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check if any pattern matches
        original_content = content
        for pattern in patterns:
            content = re.sub(pattern, replacement, content)
        
        # If content was changed, write it back to the file
        if content != original_content:
            print(f"  Found and fixed distance references in {file_path}")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        else:
            print(f"  No distance references found in {file_path}")
    
    print("\nAll template files processed successfully!")

if __name__ == "__main__":
    # Path to the templates directory
    templates_dir = "d:/TRIPINSIGHT/templates"
    
    print(f"Starting to fix distance references in template files...")
    fix_distance_references(templates_dir)
    
    print("\nDone! All distance references have been updated to 'Nearby attraction'.")