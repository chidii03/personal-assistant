# utils.py
from datetime import datetime

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def format_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")

def format_time(time_str):
    return datetime.strptime(time_str, "%H:%M").strftime("%H:%M")