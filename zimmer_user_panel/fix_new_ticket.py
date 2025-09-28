import re

# Read the current support.tsx file
with open('pages/support.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the new ticket creation to use the parsing function
old_new_ticket_logic = '''      // Convert backend ticket format to frontend format
      const newTicketData: Ticket = {
        id: createdTicket.id,
        subject: createdTicket.subject,
        category: newTicket.category, // Keep the category from form
        status: createdTicket.status,
        priority: createdTicket.importance,
        created_at: createdTicket.created_at,
        updated_at: createdTicket.updated_at,
        messages: [{
          id: Date.now(),
          content: createdTicket.message,
          is_from_user: true,
          created_at: createdTicket.created_at
        }]
      };'''

new_new_ticket_logic = '''      // Convert backend ticket format to frontend format
      const newTicketData: Ticket = {
        id: createdTicket.id,
        subject: createdTicket.subject,
        category: newTicket.category, // Keep the category from form
        status: createdTicket.status,
        priority: createdTicket.importance,
        created_at: createdTicket.created_at,
        updated_at: createdTicket.updated_at,
        messages: parseTicketMessages(createdTicket.message, createdTicket.id, createdTicket.created_at)
      };'''

# Replace the new ticket logic
content = content.replace(old_new_ticket_logic, new_new_ticket_logic)

# Write the updated content
with open('pages/support.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("New ticket creation logic fixed successfully!")
