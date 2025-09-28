import re

# Read the current support.tsx file
with open('pages/support.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Add a simple test to force different colors
test_message_display = '''                {selectedTicket.messages.map((message, index) => {
                  console.log('Message:', message.content, 'is_from_user:', message.is_from_user, 'id:', message.id, 'index:', index);
                  // Force different colors for testing
                  const isUser = index === 0; // First message is always user
                  return (
                    <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs p-3 rounded-xl ${
                        isUser
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        <p>{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          isUser ? 'text-purple-100' : 'text-gray-500'
                        }`}>
                          {new Date(message.created_at).toLocaleString('fa-IR')}
                        </p>
                      </div>
                    </div>
                  );
                })}'''

# Find and replace the message display
old_pattern = r'\{selectedTicket\.messages\.map\(message => \{[\s\S]*?\}\)\}'
content = re.sub(old_pattern, test_message_display, content)

# Write the updated content
with open('pages/support.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Test styling applied successfully!")
