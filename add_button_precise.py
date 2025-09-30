import re
import os

file_path = 'zimmermanagement/zimmer-admin-dashboard/pages/automations.tsx'

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the operations section with the exact button structure
    # Look for the div with the three buttons (eye, pencil, trash)
    operations_pattern = r'(<div className="flex space-x-2">\s*<button[^>]*>\s*<EyeIcon[^>]*/>\s*</button>\s*<button[^>]*>\s*<PencilIcon[^>]*/>\s*</button>\s*<button[^>]*>\s*<TrashIcon[^>]*/>\s*</button>\s*</div>)'
    
    generate_token_button = '''<div className="flex space-x-2">
                        <button
                          onClick={() => handleGenerateToken(automation.id)}
                          className="text-green-600 hover:text-green-900"
                          title="Generate Service Token"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1721 9z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => openEditForm(automation)}
                          className="text-indigo-600 hover:text-indigo-900"
                          title="View"
                        >
                          <EyeIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => openEditForm(automation)}
                          className="text-indigo-600 hover:text-indigo-900"
                          title="Edit"
                        >
                          <PencilIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            setSelectedAutomation(automation);
                            setShowDeleteConfirm(true);
                          }}
                          className="text-red-600 hover:text-red-900"
                          title="Delete"
                        >
                          <TrashIcon className="w-4 h-4" />
                        </button>
                      </div>'''
    
    new_content = re.sub(operations_pattern, generate_token_button, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('✅ Added generate token button to operations')
    else:
        print('❌ Could not find operations section to replace')
        # Let's try a simpler approach - just add the button before the existing buttons
        simple_pattern = r'(<button\s+onClick=\{\(\) => openEditForm\(automation\)\}[^>]*>\s*<EyeIcon[^>]*/>\s*</button>)'
        simple_button = '''<button
                          onClick={() => handleGenerateToken(automation.id)}
                          className="text-green-600 hover:text-green-900"
                          title="Generate Service Token"
                        >
                          🔑
                        </button>
                        <button
                          onClick={() => openEditForm(automation)}
                          className="text-indigo-600 hover:text-indigo-900"
                          title="View"
                        >
                          <EyeIcon className="w-4 h-4" />
                        </button>'''
        
        new_content = re.sub(simple_pattern, simple_button, content, flags=re.DOTALL)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print('✅ Added generate token button to operations (simple method)')
        else:
            print('❌ Could not find any button to replace')
else:
    print(f'❌ File not found: {file_path}')
