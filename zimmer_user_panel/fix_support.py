import re

# Read the current support.tsx file
with open('pages/support.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Add the message parsing function after the imports
parsing_function = '''
// Parse concatenated ticket messages into individual messages
const parseTicketMessages = (messageString: string, ticketId: number, createdAt: string) => {
  const messages = [];
  
  // Split by the separator pattern "--- Reply from [Name] ---"
  const parts = messageString.split(/\\n\\n--- Reply from .+ ---\\n/);
  
  // First part is the original user message
  if (parts[0].trim()) {
    messages.push({
      id: `${ticketId}-0`,
      content: parts[0].trim(),
      is_from_user: true,
      created_at: createdAt
    });
  }
  
  // Parse subsequent parts (admin replies)
  for (let i = 1; i < parts.length; i++) {
    if (parts[i].trim()) {
      messages.push({
        id: `${ticketId}-${i}`,
        content: parts[i].trim(),
        is_from_user: false, // Admin replies
        created_at: createdAt
      });
    }
  }
  
  return messages;
};
'''

# Insert the parsing function after the imports
content = content.replace(
  'export default function SupportPage() {',
  parsing_function + '\n\nexport default function SupportPage() {'
)

# Update the fetchTickets function to use the parsing function
old_fetch_logic = '''        // Convert backend tickets to frontend format
        const formattedTickets: Ticket[] = data.tickets.map((ticket: any) => ({
          id: ticket.id,
          subject: ticket.subject,
          category: 'tech', // Default category since backend doesn't store this
          status: ticket.status,
          priority: ticket.importance,
          created_at: ticket.created_at,
          updated_at: ticket.updated_at,
          messages: [{
            id: Date.now(),
            content: ticket.message,
            is_from_user: true,
            created_at: ticket.created_at
          }]
        }));'''

new_fetch_logic = '''        // Convert backend tickets to frontend format
        const formattedTickets: Ticket[] = data.tickets.map((ticket: any) => ({
          id: ticket.id,
          subject: ticket.subject,
          category: 'tech', // Default category since backend doesn't store this
          status: ticket.status,
          priority: ticket.importance,
          created_at: ticket.created_at,
          updated_at: ticket.updated_at,
          messages: parseTicketMessages(ticket.message, ticket.id, ticket.created_at)
        }));'''

content = content.replace(old_fetch_logic, new_fetch_logic)

# Write the fixed content back
with open('pages/support.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Support page fixed successfully!")
