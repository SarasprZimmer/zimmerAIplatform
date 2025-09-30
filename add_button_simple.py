import re
import os

file_path = 'zimmermanagement/zimmer-admin-dashboard/pages/automations.tsx'

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the operations section and add the generate token button
    # Look for the edit button and add the generate token button before it
    edit_button_pattern = r'(<button\s+onClick=\{\(\) => setShowEditForm\(true\)\}[^>]*>.*?ویرایش.*?</button>)'
    
    generate_token_button = '''<button
                    onClick={() => handleGenerateToken(automation.id)}
                    className="px-3 py-1 text-xs font-medium text-green-600 bg-green-100 rounded-md hover:bg-green-200 focus:outline-none focus:ring-2 focus:ring-green-500"
                    title="Generate Service Token"
                  >
                    🔑 Generate Token
                  </button>
                  <button
                    onClick={() => setShowEditForm(true)}
                    className="px-3 py-1 text-xs font-medium text-blue-600 bg-blue-100 rounded-md hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500"'''
    
    new_content = re.sub(edit_button_pattern, generate_token_button, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('✅ Added generate token button to operations')
    else:
        print('❌ Could not find edit button to replace')
        # Let's try a different approach - find the operations section
        operations_pattern = r'(<div className="flex space-x-2">.*?<button[^>]*>.*?ویرایش.*?</button>)'
        generate_token_button = '''<div className="flex space-x-2">
                    <button
                      onClick={() => handleGenerateToken(automation.id)}
                      className="px-3 py-1 text-xs font-medium text-green-600 bg-green-100 rounded-md hover:bg-green-200 focus:outline-none focus:ring-2 focus:ring-green-500"
                      title="Generate Service Token"
                    >
                      🔑 Generate Token
                    </button>
                    <button
                      onClick={() => setShowEditForm(true)}
                      className="px-3 py-1 text-xs font-medium text-blue-600 bg-blue-100 rounded-md hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500"'''
        
        new_content = re.sub(operations_pattern, generate_token_button, content, flags=re.DOTALL)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print('✅ Added generate token button to operations (alternative method)')
        else:
            print('❌ Could not find operations section to replace')
else:
    print(f'❌ File not found: {file_path}')
