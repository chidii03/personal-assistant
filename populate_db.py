import sqlite3
from datetime import datetime, timedelta
from faker import Faker
import random
from database import Database

fake = Faker()

def populate_db():
    db = Database()

    # Populate 500 contacts
    for _ in range(500):
        name = fake.name()
        phone = fake.phone_number()
        email = fake.email()
        address = fake.address().replace('\n', ', ')
        db.add_contact(name, phone, email, address)

    # Populate 1000 meetings
    for _ in range(1000):
        meeting_date = (datetime.utcnow() + timedelta(hours=1) + timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d')  # UTC+1, 60 days range
        meeting_time = fake.time(pattern="%H:%M")
        location = fake.city()
        description = fake.sentence()
        
        meeting_id = db.add_meeting(meeting_date, meeting_time, location, description)
        
        reminder_date = (datetime.strptime(meeting_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        db.add_reminder(meeting_id, reminder_date)

    print("Database populated successfully with 500 contacts, 1000 meetings, and 1000 reminders.")

if __name__ == "__main__":
    populate_db()