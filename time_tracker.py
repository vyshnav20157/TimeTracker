import time
import win32gui
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
import requests
from urllib.parse import urlparse

# File to store logs
LOG_FILE = "time_logs.csv"

def get_active_window_title():
    """Returns the title of the currently active window."""
    window = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(window)

def get_active_url():
    """Fetch the active URL from the local server and extract the domain."""
    try:
        response = requests.get("http://localhost:5000/get_url")
        if response.status_code == 200:
            url = response.text
            parsed_url = urlparse(url)
            return parsed_url.netloc  # Return only the domain name
        else:
            return "URL not available"
    except requests.exceptions.RequestException:
        return "Error fetching URL"

def extract_website_or_tab(window_title, browser_name):
    """Extract website or tab title for supported browsers."""
    if " - " in window_title:
        parts = window_title.rsplit(" - ", 1)
        if browser_name in parts[-1]:
            return parts[0]  # Tab title
    return "Unknown Tab"

def categorize_window(window_title):
    """Categorize the window based on its title and fetch the domain."""
    if "Edge" or "Brave" in window_title:
        return "Browser", get_active_url()
    else:
        return "Application", "N/A"

def log_data(data):
    """Log data to a CSV file."""
    if not os.path.exists(LOG_FILE):
        df = pd.DataFrame(columns=["Application", "Category", "Detail", "Start Time", "End Time", "Duration (seconds)"])
        df.to_csv(LOG_FILE, index=False)
    df = pd.read_csv(LOG_FILE)
    df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)

def plot_browser_based():
    """Generate and display a plot for time spent on each website."""
    if not os.path.exists(LOG_FILE):
        print("No logs found to generate graph.")
        return
    df = pd.read_csv(LOG_FILE)
    browser_data = df[df['Category'] == 'Browser']
    time_spent_per_site = browser_data.groupby("Detail")["Duration (seconds)"].sum()
    
    plt.figure(figsize=(10, 6))
    time_spent_per_site.plot(kind='bar', color='skyblue')
    plt.title("Time Spent on Each Website")
    plt.xlabel("Website (Domain)")
    plt.ylabel("Time (seconds)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def plot_category_based():
    """Generate and display a pie chart for time spent by category."""
    if not os.path.exists(LOG_FILE):
        print("No logs found to generate graph.")
        return
    df = pd.read_csv(LOG_FILE)
    time_spent_per_category = df.groupby("Category")["Duration (seconds)"].sum()
    
    plt.figure(figsize=(8, 6))
    plt.pie(time_spent_per_category, labels=time_spent_per_category.index, autopct='%1.1f%%', startangle=140)
    plt.title("Time Spent by Category")
    plt.show()

def track_time():
    active_window = None
    start_time = None
    logs = []

    try:
        while True:
            current_window = get_active_window_title()
            if current_window != active_window:
                end_time = datetime.now()
                if active_window:
                    duration = (end_time - start_time).total_seconds()
                    category, detail = categorize_window(active_window)
                    logs.append({
                        "Application": active_window,
                        "Category": category,
                        "Detail": detail,
                        "Start Time": start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        "End Time": end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        "Duration (seconds)": duration
                    })
                    print(f"Tracked: {active_window} ({category} - {detail}) for {duration:.2f} seconds.")
                active_window = current_window
                start_time = datetime.now()

            time.sleep(1)  # Check every second

    except KeyboardInterrupt:
        print("\nTracking stopped. Saving logs...")
        log_data(logs)
        print("Logs saved to time_logs.csv")

if __name__ == "__main__":
    print("Time Tracker Started. Press Ctrl+C to stop.")
    print("Commands:")
    print("  'track': Start tracking time.")
    print("  'plot_browser': Plot browser-based time spent.")
    print("  'plot_category': Plot category-based time spent.")
    print("  'exit': Exit the program.")

    while True:
        command = input("Enter command: ").strip().lower()
        if command == "track":
            track_time()
        elif command == "plot_browser":
            plot_browser_based()
        elif command == "plot_category":
            plot_category_based()
        elif command == "exit":
            print("Exiting...")
            break
        else:
            print("Unknown command. Please try again.")
