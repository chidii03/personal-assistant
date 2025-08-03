# database.py
import sqlite3
import os
import sys
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        """
        Initializes the database connection. The database file is placed in a
        persistent location (e.g., the user's home directory) to ensure data
        is saved between application runs, especially after PyInstaller packaging.
        """
        # Determine the base path for the database file
        # This will be a persistent location like the user's home directory
        try:
            # Check if the application is running as a PyInstaller bundle
            if sys.frozen:
                app_data_dir = os.path.join(os.path.expanduser('~'), '.personal_assistant_app')
            else:
                # If running as a normal script, save in the local directory
                app_data_dir = os.path.dirname(os.path.abspath(__file__))
        except Exception as e:
            # Fallback for unexpected errors
            app_data_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create the directory if it doesn't exist
        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir)
        
        db_path = os.path.join(app_data_dir, 'personal_assistant.db')
        
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Creates tables if they don't exist. This will not overwrite existing data."""
        # Note: The "DROP TABLE" command was removed to prevent data loss on startup.
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT
        )
    """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            location TEXT,
            description TEXT
        )
    """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER,
            reminder_date TEXT NOT NULL,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        )
    """)
        self.conn.commit()

    def add_contact(self, name, phone, email, address):
        self.cursor.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)", (name, phone, email, address))
        self.conn.commit()

    def add_meeting(self, date, time, location, description):
        self.cursor.execute("INSERT INTO meetings (date, time, location, description) VALUES (?, ?, ?, ?)", (date, time, location, description))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_reminder(self, meeting_id, reminder_date):
        self.cursor.execute("INSERT INTO reminders (meeting_id, reminder_date) VALUES (?, ?)", (meeting_id, reminder_date))
        self.conn.commit()

    def get_contacts(self):
        self.cursor.execute("SELECT * FROM contacts")
        return self.cursor.fetchall()

    def get_contact_by_id(self, contact_id):
        self.cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        return self.cursor.fetchone()

    def get_meetings(self):
        self.cursor.execute("SELECT * FROM meetings")
        return self.cursor.fetchall()

    def get_meeting_by_id(self, meeting_id):
        self.cursor.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
        return self.cursor.fetchone()

    def get_all_reminders(self):
        self.cursor.execute("SELECT * FROM reminders")
        return self.cursor.fetchall()

    def get_reminders(self, date):
        self.cursor.execute("SELECT m.* FROM meetings m JOIN reminders r ON m.id = r.meeting_id WHERE r.reminder_date = ?", (date,))
        return self.cursor.fetchall()

    def delete_contact(self, contact_id):
        self.cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        self.conn.commit()

    def delete_meeting(self, meeting_id):
        self.cursor.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
        self.cursor.execute("DELETE FROM reminders WHERE meeting_id = ?", (meeting_id,))
        self.conn.commit()

    def update_contact(self, contact_id, name, phone, email, address):
        self.cursor.execute("UPDATE contacts SET name = ?, phone = ?, email = ?, address = ? WHERE id = ?", (name, phone, email, address, contact_id))
        self.conn.commit()

    def update_meeting(self, meeting_id, date, time, location, description):
        self.cursor.execute("UPDATE meetings SET date = ?, time = ?, location = ?, description = ? WHERE id = ?", (date, time, location, description, meeting_id))
        self.conn.commit()

    def search_contacts(self, keyword):
        self.cursor.execute("SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ? OR address LIKE ?", (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        return self.cursor.fetchall()

    def search_meetings(self, keyword):
        self.cursor.execute("SELECT * FROM meetings WHERE date LIKE ? OR time LIKE ? OR location LIKE ? OR description LIKE ?", (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        return self.cursor.fetchall()

    def get_upcoming_meetings(self, days=7):
        today = datetime.now().date()
        future_date = today + timedelta(days=days)
        self.cursor.execute("SELECT * FROM meetings WHERE date BETWEEN ? AND ? ORDER BY date, time", (today.strftime('%Y-%m-%d'), future_date.strftime('%Y-%m-%d')))
        return self.cursor.fetchall()

    def __del__(self):
        self.conn.close()
