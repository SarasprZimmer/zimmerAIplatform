import re
import os

# Fix the automations.tsx file
file_path = 'zimmermanagement/zimmer-admin-dashboard/pages/automations.tsx'

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add the handleGenerateToken function before handleDelete
    if 'handleGenerateToken' not in content:
        # Find the handleDelete function and add handleGenerateToken before it
        handle_delete_pattern = r'(const handleDelete = async \(\) => \{)'
        handle_generate_token = '''const handleGenerateToken = async (id: number) => {
    try {
      const response = await api.post(`/api/admin/automations/${id}/generate-service-token`);
      if (response.data.token) {
        alert(`Service Token Generated:\\n\\n${response.data.token}\\n\\nPlease save this token securely. It will not be shown again.`);
      }
    } catch (error: any) {
      console.error('Error generating service token:', error);
      alert('Failed to generate service token');
    }
  };

  const handleDelete = async () => {'''
        
        new_content = re.sub(handle_delete_pattern, handle_generate_token, content)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print('✅ Added handleGenerateToken function to automations.tsx')
        else:
            print('❌ Could not find handleDelete function to replace')
    else:
        print('✅ handleGenerateToken function already exists')

    # Add the generate token button to the operations
    if 'handleGenerateToken' in content and 'Generate Service Token' not in content:
        # Find the operations section and add the button
        # Look for the edit button pattern
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
    else:
        print('✅ Generate token button already exists or function not found')

else:
    print(f'❌ File not found: {file_path}')

# Fix the api.ts file - add the generateAutomationServiceToken function
api_file_path = 'zimmermanagement/zimmer-admin-dashboard/lib/api.ts'

if os.path.exists(api_file_path):
    with open(api_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add the generateAutomationServiceToken function
    if 'generateAutomationServiceToken' not in content:
        # Find a good place to add the function - look for the end of the file or before the export
        export_pattern = r'(export default api;)'
        generate_token_api = '''// Generate service token for automation
export const generateAutomationServiceToken = async (id: number) => {
  const response = await api.post(`/api/admin/automations/${id}/generate-service-token`);
  return response.data;
};

export default api;'''
        
        new_content = re.sub(export_pattern, generate_token_api, content)
        
        if new_content != content:
            with open(api_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print('✅ Added generateAutomationServiceToken API function')
        else:
            print('❌ Could not find export statement to replace')
    else:
        print('✅ generateAutomationServiceToken API function already exists')

else:
    print(f'❌ API file not found: {api_file_path}')
