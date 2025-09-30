import re
import os

file_path = 'zimmermanagement/zimmer-admin-dashboard/pages/automations.tsx'

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the operations section and add the generate token button
    # Look for the edit and delete buttons
    operations_pattern = r'(<button\s+onClick=\{\(\) => handleEdit\(automation\)\}\s+className="[^"]*"\s*>\s*<PencilIcon[^>]*/>\s*</button>\s*<button\s+onClick=\{\(\) => handleDelete\(automation\.id\)\}\s+className="[^"]*"\s*>\s*<TrashIcon[^>]*/>\s*</button>)'
    
    new_operations = '''<button
                    onClick={() => handleGenerateToken(automation.id)}
                    className="inline-flex items-center px-2 py-1 text-xs font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    title="Generate Service Token"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1721 9z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleEdit(automation)}
                    className="inline-flex items-center px-2 py-1 text-xs font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(automation.id)}
                    className="inline-flex items-center px-2 py-1 text-xs font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>'''

    # Replace the operations section
    new_content = re.sub(operations_pattern, new_operations, content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('✅ Added generate token button to operations')
    else:
        print('❌ Could not find operations section to replace')
        
    # Now add the handleGenerateToken function
    # Look for the handleDelete function and add handleGenerateToken after it
    function_pattern = r'(const handleDelete = async \(id: number\) => \{.*?\}\s*;)'
    
    new_function = '''const handleGenerateToken = async (id: number) => {
    try {
      const response = await adminAPI.generateAutomationServiceToken(id);
      if (response.token) {
        // Show the token in a modal or alert
        alert(`Service Token Generated:\\n\\n${response.token}\\n\\nPlease save this token securely. It will not be shown again.`);
      }
    } catch (error) {
      console.error('Error generating service token:', error);
      alert('Failed to generate service token');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this automation?')) {
      return;
    }

    try {
      await adminAPI.deleteAutomation(id);
      setSuccessMessage('Automation deleted successfully');
      fetchAutomations();
    } catch (error) {
      console.error('Error deleting automation:', error);
      setErrorMessage('Failed to delete automation');
    }
  };'''

    # Replace the function
    new_content = re.sub(function_pattern, new_function, new_content, flags=re.DOTALL)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('✅ Added handleGenerateToken function')
    else:
        print('❌ Could not find handleDelete function to replace')
        
else:
    print(f'❌ File not found: {file_path}')
