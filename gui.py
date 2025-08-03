import tkinter as tk
from tkinter import messagebox, ttk
from database import Database
from utils import get_current_date
from datetime import datetime, timedelta

class PersonalAssistantApp:
    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.root.title("Personal Assistant (Premium Edition)")
        self.root.geometry("1100x750")

        try:
            from ttkbootstrap import Style
            self.style = Style(theme='darkly')
            self.style.configure("TButton", font=('Helvetica', 10, 'bold'), padding=8)
            self.style.configure("TLabel", font=('Helvetica', 10))
            self.style.configure("TEntry", font=('Helvetica', 10))
            self.style.configure("Treeview", rowheight=25, font=('Helvetica', 9))
            self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
            self.style.map("TButton", background=[('active', '#1e90ff')], foreground=[('active', 'white')])
        except ImportError:
            messagebox.showwarning("Theme Warning", "ttkbootstrap not found. Falling back to default styling.")
            self.style = ttk.Style()
            self.style.theme_use('clam')
            self.style.configure("TButton", background="#3498db", foreground="white", font=('Helvetica', 10, 'bold'))
            self.style.map("TButton", background=[('active', '#2980b9')])

        self.main_frame = ttk.Frame(root, padding=20, style="Card.TFrame")
        self.main_frame.pack(fill="both", expand=True)

        self.title_label = ttk.Label(self.main_frame, text="Personal Assistant", font=('Helvetica', 24, 'bold'), foreground="#ffffff", background="#2c3e50", padding=10)
        self.title_label.pack(pady=15)
        self.fade_in_title()

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.dashboard_frame = ttk.Frame(self.notebook, padding=15)
        self.contacts_frame = ttk.Frame(self.notebook, padding=15)
        self.meetings_frame = ttk.Frame(self.notebook, padding=15)
        self.reminders_frame = ttk.Frame(self.notebook, padding=15)

        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.contacts_frame, text="Contacts")
        self.notebook.add(self.meetings_frame, text="Meetings")
        self.notebook.add(self.reminders_frame, text="Reminders")

        self.create_dashboard_tab()
        self.setup_contacts_tab()
        self.setup_meetings_tab()
        self.setup_reminders_tab()

        self.menu = tk.Menu(root, font=('Helvetica', 10))
        self.root.config(menu=self.menu)

        self.contacts_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Contacts", menu=self.contacts_menu)
        self.contacts_menu.add_command(label="Add New Contact", command=self.add_contact_window)
        self.contacts_menu.add_command(label="Edit Selected Contact", command=self.edit_selected_contact_from_tree)
        self.contacts_menu.add_command(label="Delete Selected Contact", command=self.delete_selected_contact_from_tree)
        self.contacts_menu.add_separator()
        self.contacts_menu.add_command(label="Refresh Contacts", command=self.refresh_contacts_table)

        self.meetings_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Meetings/Appointments", menu=self.meetings_menu)
        self.meetings_menu.add_command(label="Schedule New Meeting", command=self.add_meeting_window)
        self.meetings_menu.add_command(label="Edit Selected Meeting", command=self.edit_selected_meeting_from_tree)
        self.meetings_menu.add_command(label="Delete Selected Meeting", command=self.delete_selected_meeting_from_tree)
        self.meetings_menu.add_separator()
        self.meetings_menu.add_command(label="Refresh Meetings", command=self.refresh_meetings_table)

        self.reminders_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Reminders", menu=self.reminders_menu)
        self.reminders_menu.add_command(label="View Today's Reminders", command=self.show_reminders)
        self.reminders_menu.add_command(label="Refresh Reminders", command=self.refresh_reminders_table)

        self.refresh_all_tables()
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def fade_in_title(self, alpha=0.0):
        alpha += 0.05
        self.title_label.configure(foreground=f"#{int(255 * alpha):02x}{int(255 * alpha):02x}{int(255 * alpha):02x}")
        if alpha < 1.0:
            self.root.after(50, self.fade_in_title, alpha)

    def on_tab_change(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Dashboard":
            self.update_dashboard_stats()
        elif selected_tab == "Contacts":
            self.refresh_contacts_table()
        elif selected_tab == "Meetings":
            self.refresh_meetings_table()
        elif selected_tab == "Reminders":
            self.refresh_reminders_table()

    def create_dashboard_tab(self):
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(self.dashboard_frame, text="Dashboard Overview", font=("Helvetica", 22, "bold"), foreground="#2c3e50").grid(row=0, column=0, pady=20)

        stats_frame = ttk.Frame(self.dashboard_frame, relief="raised", padding=20)
        stats_frame.grid(row=1, column=0, pady=20, padx=50, sticky="ew")
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)

        self.total_contacts_label = ttk.Label(stats_frame, text="Total Contacts: N/A", font=("Helvetica", 12))
        self.total_contacts_label.grid(row=0, column=0, padx=15, pady=10)
        self.total_meetings_label = ttk.Label(stats_frame, text="Total Meetings: N/A", font=("Helvetica", 12))
        self.total_meetings_label.grid(row=0, column=1, padx=15, pady=10)
        self.upcoming_meetings_label = ttk.Label(stats_frame, text="Upcoming Meetings (7 days): N/A", font=("Helvetica", 12))
        self.upcoming_meetings_label.grid(row=0, column=2, padx=15, pady=10)

        quick_actions_frame = ttk.Frame(self.dashboard_frame, padding=15)
        quick_actions_frame.grid(row=2, column=0, pady=30, sticky="ew")
        quick_actions_frame.grid_columnconfigure(0, weight=1)
        quick_actions_frame.grid_columnconfigure(1, weight=1)
        quick_actions_frame.grid_columnconfigure(2, weight=1)

        ttk.Button(quick_actions_frame, text="Add New Contact", command=self.add_contact_window).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(quick_actions_frame, text="Schedule Meeting", command=self.add_meeting_window).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(quick_actions_frame, text="View Reminders", command=lambda: self.notebook.select(self.reminders_frame)).grid(row=0, column=2, padx=10, pady=5)

    def setup_contacts_tab(self):
        self.contacts_frame.grid_columnconfigure(0, weight=1)
        search_frame = ttk.Frame(self.contacts_frame)
        search_frame.grid(row=0, column=0, pady=10, sticky="ew")
        self.contacts_search_entry = ttk.Entry(search_frame, width=35)
        self.contacts_search_entry.insert(0, "Search for Contacts...")
        self.contacts_search_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.contacts_search_entry, "Search for Contacts..."))
        self.contacts_search_entry.bind("<FocusOut>", lambda event: self.set_placeholder(self.contacts_search_entry, "Search for Contacts..."))
        self.contacts_search_entry.bind("<Return>", lambda event: self.search_contacts_table())
        self.contacts_search_entry.grid(row=0, column=1, padx=(0, 5), pady=5)
        ttk.Button(search_frame, text="Search", command=self.search_contacts_table).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(search_frame, text="Add New", command=self.add_contact_window).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(search_frame, text="Refresh", command=self.refresh_contacts_table).grid(row=0, column=4, padx=5, pady=5)

        table_container = ttk.Frame(self.contacts_frame)
        table_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.contacts_frame.grid_rowconfigure(1, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        self.contacts_tree = ttk.Treeview(table_container, columns=("ID", "Name", "Phone", "Email", "Address"), show="headings")
        self.contacts_tree.grid(row=0, column=0, sticky="nsew")
        for col in ["ID", "Name", "Phone", "Email", "Address"]:
            self.contacts_tree.heading(col, text=col, anchor="center")
            self.contacts_tree.column(col, anchor="center")
        self.contacts_tree.column("ID", width=60)
        self.contacts_tree.column("Name", width=180)
        self.contacts_tree.column("Phone", width=150)
        self.contacts_tree.column("Email", width=200)
        self.contacts_tree.column("Address", width=300)

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.contacts_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.contacts_tree.configure(yscrollcommand=scrollbar.set)
        self.contacts_tree.bind("<Double-1>", self.edit_selected_contact_from_tree)
        self.contacts_tree.bind("<Button-3>", self.show_contact_context_menu)

    def setup_meetings_tab(self):
        self.meetings_frame.grid_columnconfigure(0, weight=1)
        search_frame = ttk.Frame(self.meetings_frame)
        search_frame.grid(row=0, column=0, pady=10, sticky="ew")
        self.meetings_search_entry = ttk.Entry(search_frame, width=35)
        self.meetings_search_entry.insert(0, "Search for Meetings...")
        self.meetings_search_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.meetings_search_entry, "Search for Meetings..."))
        self.meetings_search_entry.bind("<FocusOut>", lambda event: self.set_placeholder(self.meetings_search_entry, "Search for Meetings..."))
        self.meetings_search_entry.bind("<Return>", lambda event: self.search_meetings_table())
        self.meetings_search_entry.grid(row=0, column=1, padx=(0, 5), pady=5)
        ttk.Button(search_frame, text="Search", command=self.search_meetings_table).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(search_frame, text="Schedule New", command=self.add_meeting_window).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(search_frame, text="Refresh", command=self.refresh_meetings_table).grid(row=0, column=4, padx=5, pady=5)

        table_container = ttk.Frame(self.meetings_frame)
        table_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.meetings_frame.grid_rowconfigure(1, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        self.meetings_tree = ttk.Treeview(table_container, columns=("ID", "Date", "Time", "Location", "Description"), show="headings")
        self.meetings_tree.grid(row=0, column=0, sticky="nsew")
        for col in ["ID", "Date", "Time", "Location", "Description"]:
            self.meetings_tree.heading(col, text=col, anchor="center")
            self.meetings_tree.column(col, anchor="center")
        self.meetings_tree.column("ID", width=60)
        self.meetings_tree.column("Date", width=120)
        self.meetings_tree.column("Time", width=100)
        self.meetings_tree.column("Location", width=180)
        self.meetings_tree.column("Description", width=280)

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.meetings_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.meetings_tree.configure(yscrollcommand=scrollbar.set)
        self.meetings_tree.bind("<Double-1>", self.edit_selected_meeting_from_tree)
        self.meetings_tree.bind("<Button-3>", self.show_meeting_context_menu)

    def setup_reminders_tab(self):
        self.reminders_frame.grid_columnconfigure(0, weight=1)
        ttk.Label(self.reminders_frame, text="Upcoming Reminders", font=('Helvetica', 16, 'bold')).grid(row=0, column=0, pady=15, sticky="ew")

        table_container = ttk.Frame(self.reminders_frame)
        table_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.reminders_frame.grid_rowconfigure(1, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(0, weight=1)

        self.reminders_tree = ttk.Treeview(table_container, columns=("Meeting ID", "Date", "Time", "Location", "Description", "Reminder Date"), show="headings")
        self.reminders_tree.grid(row=0, column=0, sticky="nsew")
        for col in self.reminders_tree["columns"]:
            self.reminders_tree.heading(col, text=col, anchor="center")
            self.reminders_tree.column(col, anchor="center")
        self.reminders_tree.column("Meeting ID", width=80)
        self.reminders_tree.column("Date", width=100)
        self.reminders_tree.column("Time", width=80)
        self.reminders_tree.column("Location", width=150)
        self.reminders_tree.column("Description", width=250)
        self.reminders_tree.column("Reminder Date", width=120)

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.reminders_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.reminders_tree.configure(yscrollcommand=scrollbar.set)

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)

    def set_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)

    def refresh_all_tables(self):
        self.refresh_contacts_table()
        self.refresh_meetings_table()
        self.refresh_reminders_table()
        self.update_dashboard_stats()

    def refresh_contacts_table(self):
        for item in self.contacts_tree.get_children():
            self.contacts_tree.delete(item)
        contacts = self.db.get_contacts()
        for contact in contacts:
            self.contacts_tree.insert("", "end", values=contact)

    def search_contacts_table(self):
        keyword = self.contacts_search_entry.get().strip()
        if keyword == "Search for Contacts..." or not keyword:
            self.refresh_contacts_table()
            return
        for item in self.contacts_tree.get_children():
            self.contacts_tree.delete(item)
        results = self.db.search_contacts(keyword)
        for contact in results:
            self.contacts_tree.insert("", "end", values=contact)

    def refresh_meetings_table(self):
        for item in self.meetings_tree.get_children():
            self.meetings_tree.delete(item)
        meetings = self.db.get_meetings()
        for meeting in meetings:
            self.meetings_tree.insert("", "end", values=meeting)

    def search_meetings_table(self):
        keyword = self.meetings_search_entry.get().strip()
        if keyword == "Search for Meetings..." or not keyword:
            self.refresh_meetings_table()
            return
        for item in self.meetings_tree.get_children():
            self.meetings_tree.delete(item)
        results = self.db.search_meetings(keyword)
        for meeting in results:
            self.meetings_tree.insert("", "end", values=meeting)

    def refresh_reminders_table(self):
        for item in self.reminders_tree.get_children():
            self.reminders_tree.delete(item)
        today = datetime.utcnow() + timedelta(hours=1)  # Adjust to UTC+1 for Nigeria
        future_date = today + timedelta(days=7)
        self.db.cursor.execute("""
            SELECT m.id, m.date, m.time, m.location, m.description, r.reminder_date
            FROM meetings m
            JOIN reminders r ON m.id = r.meeting_id
            WHERE r.reminder_date BETWEEN ? AND ?
            ORDER BY r.reminder_date
        """, (today.date().strftime('%Y-%m-%d'), future_date.date().strftime('%Y-%m-%d')))
        reminders = self.db.cursor.fetchall()
        for reminder in reminders:
            self.reminders_tree.insert("", "end", values=reminder)
        if not reminders:
            self.reminders_tree.insert("", "end", values=("No Reminders", "", "", "", "", ""))

    def show_reminders(self):
        today_date = get_current_date()
        reminders = self.db.get_reminders(today_date)
        if reminders:
            reminder_text = "Reminders for Today:\n\n"
            for reminder in reminders:
                reminder_text += f"Meeting ID: {reminder[0]}\nDate: {reminder[1]}\nTime: {reminder[2]}\nLocation: {reminder[3]}\nDescription: {reminder[4]}\n\n"
            messagebox.showinfo("Today's Reminders", reminder_text)
        else:
            messagebox.showinfo("Today's Reminders", "No reminders for today.")

    def add_contact_window(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Add New Contact")
        add_win.geometry("450x350")
        add_win.resizable(False, False)
        add_win.transient(self.root)
        add_win.grab_set()

        add_win.grid_columnconfigure(0, weight=1)
        add_win.grid_columnconfigure(1, weight=0)
        add_win.grid_columnconfigure(2, weight=0)
        add_win.grid_columnconfigure(3, weight=1)

        row_idx = 0
        ttk.Label(add_win, text="Name:").grid(row=row_idx, column=1, padx=10, pady=10, sticky="e")
        name_entry = ttk.Entry(add_win, width=35)
        name_entry.grid(row=row_idx, column=2, padx=10, pady=10)

        row_idx += 1
        ttk.Label(add_win, text="Phone:").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        phone_entry = ttk.Entry(add_win, width=35)
        phone_entry.grid(row=row_idx, column=2, padx=10, pady=5)

        row_idx += 1
        ttk.Label(add_win, text="Email:").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        email_entry = ttk.Entry(add_win, width=35)
        email_entry.grid(row=row_idx, column=2, padx=10, pady=5)

        row_idx += 1
        ttk.Label(add_win, text="Address:").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        address_entry = ttk.Entry(add_win, width=35)
        address_entry.grid(row=row_idx, column=2, padx=10, pady=5)

        def perform_add_contact():
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            address = address_entry.get().strip()
            if not name:
                messagebox.showerror("Input Error", "Name cannot be empty!", parent=add_win)
                return
            self.db.add_contact(name, phone, email, address)
            messagebox.showinfo("Success", "Contact added successfully!", parent=add_win)
            self.refresh_contacts_table()
            add_win.destroy()

        ttk.Button(add_win, text="Add Contact", command=perform_add_contact).grid(row=row_idx + 1, column=1, columnspan=2, pady=20)

    def edit_selected_contact_from_tree(self, event=None):
        selected_item = self.contacts_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a contact to edit.")
            return
        contact_id = self.contacts_tree.item(selected_item, "values")[0]
        self._open_edit_contact_window(contact_id)

    def _open_edit_contact_window(self, contact_id):
        contact = self.db.get_contact_by_id(contact_id)
        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Edit Contact (ID: {contact_id})")
        edit_win.geometry("450x350")
        edit_win.resizable(False, False)
        edit_win.transient(self.root)
        edit_win.grab_set()

        edit_win.grid_columnconfigure(0, weight=1)
        edit_win.grid_columnconfigure(1, weight=0)
        edit_win.grid_columnconfigure(2, weight=0)
        edit_win.grid_columnconfigure(3, weight=1)

        row_idx = 0
        ttk.Label(edit_win, text="Name:").grid(row=row_idx, column=1, padx=10, pady=10, sticky="e")
        name_entry = ttk.Entry(edit_win, width=35)
        name_entry.insert(0, contact[1])
        name_entry.grid(row=row_idx, column=2, padx=10, pady=10)

        row_idx += 1
        ttk.Label(edit_win, text="Phone:").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        phone_entry = ttk.Entry(edit_win, width=35)
        phone_entry.insert(0, contact[2])
        phone_entry.grid(row=row_idx, column=2, padx=10, pady=5)

        row_idx += 1
        ttk.Label(edit_win, text="Email:").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        email_entry = ttk.Entry(edit_win, width=35)
        email_entry.insert(0, contact[3])
        email_entry.grid(row=row_idx, column=2, padx=10, pady=5)

        row_idx += 1
        ttk.Label(edit_win, text="Address:").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        address_entry = ttk.Entry(edit_win, width=35)
        address_entry.insert(0, contact[4])
        address_entry.grid(row=row_idx, column=2, padx=10, pady=5)

        def perform_update_contact():
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            address = address_entry.get().strip()
            if not name:
                messagebox.showerror("Input Error", "Name cannot be empty!", parent=edit_win)
                return
            self.db.update_contact(contact_id, name, phone, email, address)
            messagebox.showinfo("Success", "Contact updated successfully!", parent=edit_win)
            self.refresh_contacts_table()
            edit_win.destroy()

        ttk.Button(edit_win, text="Update Contact", command=perform_update_contact).grid(row=row_idx + 1, column=1, columnspan=2, pady=20)

    def delete_selected_contact_from_tree(self):
        selected_item = self.contacts_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a contact to delete.")
            return
        contact_id = self.contacts_tree.item(selected_item, "values")[0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete contact ID {contact_id}?"):
            self.db.delete_contact(contact_id)
            self.refresh_contacts_table()

    def show_contact_context_menu(self, event):
        item = self.contacts_tree.identify_row(event.y)
        if item:
            self.contacts_tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Edit Contact", command=self.edit_selected_contact_from_tree)
            menu.add_command(label="Delete Contact", command=self.delete_selected_contact_from_tree)
            menu.post(event.x_root, event.y_root)

    def add_meeting_window(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Schedule New Meeting")
        add_win.geometry("450x380")
        add_win.resizable(False, False)
        add_win.transient(self.root)
        add_win.grab_set()

        add_win.grid_columnconfigure(0, weight=1)
        add_win.grid_columnconfigure(1, weight=0)
        add_win.grid_columnconfigure(2, weight=0)
        add_win.grid_columnconfigure(3, weight=1)

        row_idx = 0
        ttk.Label(add_win, text="Date (YYYY-MM-DD):").grid(row=row_idx, column=1, padx=10, pady=10, sticky="e")
        date_entry = ttk.Entry(add_win, width=35)
        current_time = datetime.utcnow() + timedelta(hours=1)  # Adjust to UTC+1 for Nigeria
        date_entry.insert(0, current_time.strftime('%Y-%m-%d'))
        date_entry.grid(row=row_idx, column=2, padx=10, pady=10)

        row_idx += 1
        ttk.Label(add_win, text="Time (HH:MM):").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        time_entry = ttk.Entry(add_win, width=35)
        time_entry.insert(0, current_time.strftime('%H:%M'))  # Set to current time in Nigeria (approx. 02:56)
        time_entry.grid(row=row_idx, column=2, padx=10, pady=5)

        row_idx += 1
        ttk.Label(add_win, text="Location:").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        location_entry = ttk.Entry(add_win, width=35)
        location_entry.grid(row=row_idx, column=2, padx=10, pady=5)

        row_idx += 1
        ttk.Label(add_win, text="Description:").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        description_entry = ttk.Entry(add_win, width=35)
        description_entry.grid(row=row_idx, column=2, padx=10, pady=5)

        row_idx += 1
        ttk.Label(add_win, text="Reminder Date (YYYY-MM-DD):").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        reminder_date_entry = ttk.Entry(add_win, width=35)
        reminder_date_entry.insert(0, current_time.strftime('%Y-%m-%d'))
        reminder_date_entry.grid(row=row_idx, column=2, padx=10, pady=5)

        def perform_add_meeting():
            date = date_entry.get().strip()
            time = time_entry.get().strip()
            location = location_entry.get().strip()
            description = description_entry.get().strip()
            reminder_date = reminder_date_entry.get().strip()

            if not all([date, time, description, reminder_date]):
                messagebox.showerror("Input Error", "All fields are required!", parent=add_win)
                return
            try:
                datetime.strptime(date, '%Y-%m-%d')
                datetime.strptime(time, '%H:%M')
                datetime.strptime(reminder_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Input Error", "Invalid format! Use YYYY-MM-DD for dates and HH:MM for time.", parent=add_win)
                return

            meeting_id = self.db.add_meeting(date, time, location, description)
            self.db.add_reminder(meeting_id, reminder_date)
            messagebox.showinfo("Success", "Meeting scheduled!", parent=add_win)
            self.refresh_meetings_table()
            self.refresh_reminders_table()
            add_win.destroy()

        ttk.Button(add_win, text="Schedule Meeting", command=perform_add_meeting).grid(row=row_idx + 1, column=1, columnspan=2, pady=20)

    def edit_selected_meeting_from_tree(self, event=None):
        selected_item = self.meetings_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a meeting to edit.")
            return
        meeting_id = self.meetings_tree.item(selected_item, "values")[0]
        self._open_edit_meeting_window(meeting_id)

    def _open_edit_meeting_window(self, meeting_id):
        meeting = self.db.get_meeting_by_id(meeting_id)
        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Edit Meeting (ID: {meeting_id})")
        edit_win.geometry("450x380")
        edit_win.resizable(False, False)
        edit_win.transient(self.root)
        edit_win.grab_set()

        edit_win.grid_columnconfigure(0, weight=1)
        edit_win.grid_columnconfigure(1, weight=0)
        edit_win.grid_columnconfigure(2, weight=0)
        edit_win.grid_columnconfigure(3, weight=1)

        row_idx = 0
        ttk.Label(edit_win, text="Date (YYYY-MM-DD):").grid(row=row_idx, column=1, padx=10, pady=10, sticky="e")
        date_entry = ttk.Entry(edit_win, width=35)
        date_entry.insert(0, meeting[1])
        date_entry.grid(row=row_idx, column=2, padx=10, pady=10)

        row_idx += 1
        ttk.Label(edit_win, text="Time (HH:MM):").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        time_entry = ttk.Entry(edit_win, width=35)
        time_entry.insert(0, meeting[2])
        time_entry.grid(row=row_idx, column=2, padx=10, pady=5)

        row_idx += 1
        ttk.Label(edit_win, text="Location:").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        location_entry = ttk.Entry(edit_win, width=35)
        location_entry.insert(0, meeting[3])
        location_entry.grid(row=row_idx, column=2, padx=10, pady=5)

        row_idx += 1
        ttk.Label(edit_win, text="Description:").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        description_entry = ttk.Entry(edit_win, width=35)
        description_entry.insert(0, meeting[4])
        description_entry.grid(row=row_idx, column=2, padx=10, pady=5)

        row_idx += 1
        ttk.Label(edit_win, text="Reminder Date (YYYY-MM-DD):").grid(row=row_idx, column=1, padx=10, pady=5, sticky="e")
        reminder_date_entry = ttk.Entry(edit_win, width=35)
        self.db.cursor.execute("SELECT reminder_date FROM reminders WHERE meeting_id = ?", (meeting_id,))
        reminder_date = self.db.cursor.fetchone()
        reminder_date_entry.insert(0, reminder_date[0] if reminder_date else meeting[1])
        reminder_date_entry.grid(row=row_idx, column=2, padx=10, pady=5)

        def perform_update_meeting():
            date = date_entry.get().strip()
            time = time_entry.get().strip()
            location = location_entry.get().strip()
            description = description_entry.get().strip()
            reminder_date = reminder_date_entry.get().strip()
            if not all([date, time, description, reminder_date]):
                messagebox.showerror("Input Error", "All fields are required!", parent=edit_win)
                return
            try:
                datetime.strptime(date, '%Y-%m-%d')
                datetime.strptime(time, '%H:%M')
                datetime.strptime(reminder_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Input Error", "Invalid format! Use YYYY-MM-DD for dates and HH:MM for time.", parent=edit_win)
                return
            self.db.update_meeting(meeting_id, date, time, location, description)
            self.db.cursor.execute("UPDATE reminders SET reminder_date = ? WHERE meeting_id = ?", (reminder_date, meeting_id))
            self.db.conn.commit()
            messagebox.showinfo("Success", "Meeting updated!", parent=edit_win)
            self.refresh_meetings_table()
            self.refresh_reminders_table()
            edit_win.destroy()

        ttk.Button(edit_win, text="Update Meeting", command=perform_update_meeting).grid(row=row_idx + 1, column=1, columnspan=2, pady=20)

    def delete_selected_meeting_from_tree(self):
        selected_item = self.meetings_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a meeting to delete.")
            return
        meeting_id = self.meetings_tree.item(selected_item, "values")[0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete meeting ID {meeting_id}?"):
            self.db.delete_meeting(meeting_id)
            self.refresh_meetings_table()
            self.refresh_reminders_table()

    def show_meeting_context_menu(self, event):
        item = self.meetings_tree.identify_row(event.y)
        if item:
            self.meetings_tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Edit Meeting", command=self.edit_selected_meeting_from_tree)
            menu.add_command(label="Delete Meeting", command=self.delete_selected_meeting_from_tree)
            menu.post(event.x_root, event.y_root)

    def update_dashboard_stats(self):
        total_contacts = len(self.db.get_contacts())
        total_meetings = len(self.db.get_meetings())
        upcoming_meetings = self.db.get_upcoming_meetings(days=7)
        self.total_contacts_label.config(text=f"Total Contacts: {total_contacts}")
        self.total_meetings_label.config(text=f"Total Meetings: {total_meetings}")
        self.upcoming_meetings_label.config(text=f"Upcoming Meetings (7 days): {len(upcoming_meetings)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PersonalAssistantApp(root)
    root.mainloop()