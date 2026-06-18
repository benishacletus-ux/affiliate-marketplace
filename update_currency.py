import re
import os

def update_currency_in_templates(template_dir='templates'):
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace $ with ₹ and add * 83
                # Pattern: ${{ "%.2f"|format(variable) }}
                pattern = r'\${{ "%.2f"\|format\(([^)]+)\) }}'
                replacement = r'₹{{ "%.2f"|format(\1 * 83) }}'
                new_content = re.sub(pattern, replacement, content)
                
                # Also handle cases without spaces
                pattern2 = r'\${{ "%.2f"\|format\(([^)]+)\)}}'
                replacement2 = r'₹{{ "%.2f"|format(\1 * 83)}}'
                new_content = re.sub(pattern2, replacement2, new_content)
                
                if content != new_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated: {filepath}")

if __name__ == '__main__':
    update_currency_in_templates()