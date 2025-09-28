import re

# Read the current support.tsx file
with open('pages/support.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Add debug logging to the message display
old_message_display = '''                {selectedTicket.messages.map(message => (
                  <div key={message.id} className={`flex ${message.is_from_user ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xs p-3 rounded-xl ${
                      message.is_from_user
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      <p>{message.content}</p>
                      <p className={`text-xs mt-1 ${
                        message.is_from_user ? 'text-purple-100' : 'text-gray-500'
                      }`}>
                        {new Date(message.created_at).toLocaleString('fa-IR')}
                      </p>
                    </div>
                  </div>
                ))}'''

debug_message_display = '''                {selectedTicket.messages.map(message => {
                  console.log('Message:', message.content, 'is_from_user:', message.is_from_user, 'id:', message.id);
                  return (
                    <div key={message.id} className={`flex ${message.is_from_user ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs p-3 rounded-xl ${
                        message.is_from_user
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        <p>{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          message.is_from_user ? 'text-purple-100' : 'text-gray-500'
                        }`}>
                          {new Date(message.created_at).toLocaleString('fa-IR')}
                        </p>
                      </div>
                    </div>
                  );
                })}'''

# Replace the message display with debug version
content = content.replace(old_message_display, debug_message_display)

# Write the updated content
with open('pages/support.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Debug logging added successfully!")
