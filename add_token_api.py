import re
import os

file_path = 'zimmermanagement/zimmer-admin-dashboard/lib/api.ts'

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the deleteAutomation function and add generateAutomationServiceToken after it
    function_pattern = r'(deleteAutomation: async \(id: number\) => \{.*?\}\s*;)'
    
    new_function = '''generateAutomationServiceToken: async (id: number) => {
    const response = await api.post(`/admin/automations/${id}/generate-service-token`);
    return response.data;
  },

  deleteAutomation: async (id: number) => {
    const response = await api.delete(`/admin/automations/${id}`);
    return response.data;
  };'''

    # Replace the function
    new_content = re.sub(function_pattern, new_function, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('✅ Added generateAutomationServiceToken API function')
    else:
        print('❌ Could not find deleteAutomation function to replace')
        
else:
    print(f'❌ File not found: {file_path}')
