# fix_templates.py
import os
import re

templates_dir = 'templates'

# List of replacements to make
replacements = [
    ("url_for('login')", "url_for('customer_login')"),
    ("url_for('register')", "url_for('customer_register')"),
    ("url_for('logout')", "url_for('customer_logout')"),
]

# Walk through all template files
for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply replacements
            modified = False
            for old, new in replacements:
                if old in content:
                    content = content.replace(old, new)
                    modified = True
            
            if modified:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Fixed: {filepath}")

print("All templates fixed!")