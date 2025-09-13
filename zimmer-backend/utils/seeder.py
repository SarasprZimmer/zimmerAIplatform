from sqlalchemy.orm import Session
from models.user import User
from models.automation import Automation
from models.knowledge import KnowledgeEntry
from models.ticket import Ticket, TicketStatus
from database import SessionLocal
from utils.security import hash_password

def seed_sample_data():
    """
    Seed the database with sample data for development
    """
    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.email == "admin@zimmer.com").first()
        if not admin_user:
            admin_user = User(
                name="Admin User",
                email="admin@zimmer.com",
                phone_number="+1234567890",
                password_hash=hash_password("admin123"),
                role="manager"
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("✅ Admin user created: admin@zimmer.com / admin123")
        else:
            print("ℹ️ Admin user already exists")

        # Check if regular user already exists
        regular_user = db.query(User).filter(User.email == "user@example.com").first()
        if not regular_user:
            regular_user = User(
                name="John Doe",
                email="user@example.com",
                phone_number="+1987654321",
                password_hash=hash_password("user123"),
                role="support_staff"
            )
            db.add(regular_user)
            db.commit()
            db.refresh(regular_user)
            print("✅ Regular user created: user@example.com / user123")
        else:
            print("ℹ️ Regular user already exists")
            
        # Also create test@example.com for consistency with frontend testing
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if not test_user:
            test_user = User(
                name="Test User",
                email="test@example.com",
                phone_number="+1555555555",
                password_hash=hash_password("test123"),
                role="support_staff"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print("✅ Test user created: test@example.com / test123")
        else:
            print("ℹ️ Test user already exists")

        # Check if automations already exist
        travel_ai = db.query(Automation).filter(Automation.name == "TravelAI Assistant").first()
        if not travel_ai:
            travel_ai = Automation(
                name="TravelAI Assistant",
                description="AI-powered travel planning and visa assistance",
                pricing_type="token_per_session",
                price_per_token=100.0,
                health_status="unknown",  # Add required field
                is_listed=False  # Add required field
            )
            db.add(travel_ai)
            db.commit()
            db.refresh(travel_ai)
            print("✅ TravelAI automation created")
        else:
            print("ℹ️ TravelAI automation already exists")

        seo_agent = db.query(Automation).filter(Automation.name == "SEO Agent").first()
        if not seo_agent:
            seo_agent = Automation(
                name="SEO Agent",
                description="Automated SEO optimization and content analysis",
                pricing_type="token_per_session",
                price_per_token=150.0,
                health_status="unknown",  # Add required field
                is_listed=False  # Add required field
            )
            db.add(seo_agent)
            db.commit()
            db.refresh(seo_agent)
            print("✅ SEO Agent automation created")
        else:
            print("ℹ️ SEO Agent automation already exists")

        # Check if knowledge entries already exist
        existing_knowledge = db.query(KnowledgeEntry).filter(
            KnowledgeEntry.client_id == regular_user.id
        ).count()
        
        if existing_knowledge == 0:
            # Create sample knowledge entries
            knowledge_entries = [
                KnowledgeEntry(
                    client_id=regular_user.id,
                    category="visa",
                    answer="For tourist visas, you typically need a valid passport, completed application form, passport photos, travel itinerary, and proof of financial means. Processing time is usually 5-10 business days."
                ),
                KnowledgeEntry(
                    client_id=regular_user.id,
                    category="faq",
                    answer="Our AI assistant can help with travel planning, visa applications, and general travel inquiries. For complex cases, we'll escalate to our human support team."
                ),
                KnowledgeEntry(
                    client_id=regular_user.id,
                    category="pricing",
                    answer="Our basic plan starts at $29/month for 100 AI interactions. Premium plans with unlimited interactions start at $99/month. Custom enterprise plans are available."
                )
            ]
            
            for entry in knowledge_entries:
                db.add(entry)
            
            db.commit()
            print("✅ Sample knowledge entries created")
        else:
            print("ℹ️ Knowledge entries already exist")

        # Check if tickets already exist
        existing_tickets = db.query(Ticket).filter(
            Ticket.user_id == regular_user.id
        ).count()
        
        if existing_tickets == 0:
            # Create sample tickets
            sample_tickets = [
                Ticket(
                    user_id=regular_user.id,
                    subject="Visa Application Help",
                    message="I need assistance with my visa application process. I'm planning to travel to Europe next month and would like guidance on the required documents and procedures.",
                    status=TicketStatus.OPEN
                ),
                Ticket(
                    user_id=regular_user.id,
                    subject="AI Assistant Not Responding",
                    message="The AI assistant seems to be down or not responding to my queries. I've tried multiple times but keep getting error messages.",
                    status=TicketStatus.PENDING,
                    assigned_to=admin_user.id
                ),
                Ticket(
                    user_id=regular_user.id,
                    subject="Billing Question",
                    message="I have a question about my recent billing. I was charged for additional tokens but I believe I'm still within my plan limits.",
                    status=TicketStatus.RESOLVED,
                    assigned_to=admin_user.id
                )
            ]
            
            for ticket in sample_tickets:
                db.add(ticket)
            
            db.commit()
            print("✅ Sample tickets created")
        else:
            print("ℹ️ Tickets already exist")

        print("🎉 Sample data seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {str(e)}")
        raise
    finally:
        db.close() 