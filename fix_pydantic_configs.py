#!/usr/bin/env python3
import os
import re

def fix_pydantic_configs(file_path):
    """Fix Pydantic configurations in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping {file_path} due to encoding issues")
        return False
    
    original_content = content
    
    # Fix old Config class syntax to new ConfigDict syntax
    # Pattern: class Config:\n        from_attributes = True
    pattern = r'class Config:\s*\n\s*from_attributes = True'
    replacement = 'model_config = ConfigDict(from_attributes=True)'
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Add ConfigDict import if needed
    if 'model_config = ConfigDict' in content and 'ConfigDict' not in content:
        # Find the first import line
        lines = content.split('\n')
        import_line = None
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                import_line = i
                break
        
        if import_line is not None:
            # Add ConfigDict to existing import
            if 'from pydantic import' in lines[import_line]:
                lines[import_line] = lines[import_line].replace('from pydantic import', 'from pydantic import ConfigDict,')
            else:
                lines.insert(import_line, 'from pydantic import ConfigDict')
        else:
            # Add import at the beginning
            lines.insert(0, 'from pydantic import ConfigDict')
        
        content = '\n'.join(lines)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {file_path}")
        return True
    return False

def main():
    """Fix all Python files in the backend directory"""
    backend_dir = 'zimmer-backend'
    fixed_count = 0
    
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_pydantic_configs(file_path):
                    fixed_count += 1
    
    print(f"Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
