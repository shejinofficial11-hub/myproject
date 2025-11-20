import sqlite3
import datetime
import threading
import time
import eel
from backend.command import speak

conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()

# Calendar Functions
@eel.expose
def addEvent(title, event_datetime, description=""):
    """Add event to calendar"""
    try:
        cursor.execute("INSERT INTO events (title, datetime, description) VALUES (?, ?, ?)",
                      (title, event_datetime, description))
        conn.commit()
        speak(f"Event '{title}' has been added to your calendar.")
        return {"success": True, "message": f"Event '{title}' added successfully"}
    except Exception as e:
        print(f"Error adding event: {e}")
        speak("Sorry, I couldn't add the event to your calendar.")
        return {"success": False, "error": str(e)}

@eel.expose
def getTodayEvents():
    """Retrieve today's schedule"""
    try:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT title, datetime, description FROM events WHERE DATE(datetime) = ? ORDER BY datetime", (today,))
        events = cursor.fetchall()

        if events:
            speak(f"You have {len(events)} events scheduled for today.")
            event_list = []
            for event in events:
                event_time = datetime.datetime.strptime(event[1], "%Y-%m-%d %H:%M:%S").strftime("%I:%M %p")
                event_list.append({
                    'title': event[0],
                    'time': event_time,
                    'description': event[2]
                })
            return {"success": True, "events": event_list}
        else:
            speak("You have no events scheduled for today.")
            return {"success": True, "events": []}

    except Exception as e:
        print(f"Error getting today's events: {e}")
        speak("Sorry, I couldn't retrieve your schedule for today.")
        return {"success": False, "error": str(e)}

@eel.expose
def getUpcomingEvents(days=7):
    """Retrieve events for the next N days"""
    try:
        today = datetime.datetime.now()
        future_date = (today + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")

        cursor.execute("SELECT title, datetime, description FROM events WHERE DATE(datetime) BETWEEN ? AND ? ORDER BY datetime",
                      (today_str, future_date))
        events = cursor.fetchall()

        event_list = []
        for event in events:
            event_date = datetime.datetime.strptime(event[1], "%Y-%m-%d %H:%M:%S")
            event_str = event_date.strftime("%A, %B %d at %I:%M %p")
            event_list.append({
                'title': event[0],
                'datetime': event_str,
                'description': event[2]
            })

        return {"success": True, "events": event_list}

    except Exception as e:
        print(f"Error getting upcoming events: {e}")
        return {"success": False, "error": str(e)}

# Reminder Functions
@eel.expose
def setReminder(message, minutes_from_now):
    """Set timed reminder"""
    try:
        trigger_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes_from_now)
        trigger_time_str = trigger_time.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("INSERT INTO reminders (message, trigger_time, is_active) VALUES (?, ?, 1)",
                      (message, trigger_time_str))
        conn.commit()

        # Start background thread to check reminder
        reminder_thread = threading.Thread(target=checkReminder, args=(cursor.lastrowid,), daemon=True)
        reminder_thread.start()

        speak(f"Reminder set for {minutes_from_now} minutes from now.")
        return {"success": True, "message": f"Reminder set for {minutes_from_now} minutes"}

    except Exception as e:
        print(f"Error setting reminder: {e}")
        speak("Sorry, I couldn't set the reminder.")
        return {"success": False, "error": str(e)}

@eel.expose
def getActiveReminders():
    """Get all active reminders"""
    try:
        cursor.execute("SELECT id, message, trigger_time FROM reminders WHERE is_active = 1 ORDER BY trigger_time")
        reminders = cursor.fetchall()

        reminder_list = []
        for reminder in reminders:
            reminder_time = datetime.datetime.strptime(reminder[2], "%Y-%m-%d %H:%M:%S")
            reminder_str = reminder_time.strftime("%A, %B %d at %I:%M %p")
            reminder_list.append({
                'id': reminder[0],
                'message': reminder[1],
                'trigger_time': reminder_str
            })

        return {"success": True, "reminders": reminder_list}

    except Exception as e:
        print(f"Error getting active reminders: {e}")
        return {"success": False, "error": str(e)}

def checkReminder(reminder_id):
    """Background thread to check and trigger reminder"""
    try:
        while True:
            cursor.execute("SELECT message, trigger_time, is_active FROM reminders WHERE id = ?", (reminder_id,))
            reminder = cursor.fetchone()

            if not reminder or reminder[2] == 0:  # Reminder doesn't exist or is inactive
                break

            current_time = datetime.datetime.now()
            trigger_time = datetime.datetime.strptime(reminder[1], "%Y-%m-%d %H:%M:%S")

            if current_time >= trigger_time:
                # Trigger the reminder
                speak(f"Reminder: {reminder[0]}")

                # Mark reminder as inactive
                cursor.execute("UPDATE reminders SET is_active = 0 WHERE id = ?", (reminder_id,))
                conn.commit()
                break

            time.sleep(30)  # Check every 30 seconds

    except Exception as e:
        print(f"Error in reminder thread: {e}")

def processCalendarCommand(query):
    """Process calendar-related voice commands"""
    query_lower = query.lower()

    if any(word in query_lower for word in ["calendar", "schedule", "appointment", "meeting"]):
        if "today" in query_lower or "schedule" in query_lower:
            events = getTodayEvents()
        elif "upcoming" in query_lower or "week" in query_lower:
            events = getUpcomingEvents(7)
        else:
            getTodayEvents()
        return True

    elif "reminder" in query_lower:
        if "set" in query_lower or "create" in query_lower:
            speak("What should I remind you about?")
            # In a real implementation, you'd wait for voice input here
            message = "Remember to take a break"
            speak("In how many minutes?")
            # Again, wait for voice input
            minutes = 5
            setReminder(message, minutes)
        return True

    return False

def parseDateTimeFromQuery(query):
    """Parse date and time from natural language query"""
    # Simple implementation - in a real system, you'd use more sophisticated NLP
    query_lower = query.lower()

    # Time patterns
    if "tomorrow" in query_lower:
        date = datetime.datetime.now() + datetime.timedelta(days=1)
    elif "today" in query_lower:
        date = datetime.datetime.now()
    else:
        # Default to today
        date = datetime.datetime.now()

    # Time extraction (basic)
    if "am" in query_lower or "pm" in query_lower:
        # Extract time like "3 PM" or "10 AM"
        import re
        time_match = re.search(r'(\d{1,2})\s*(am|pm)', query_lower)
        if time_match:
            hour = int(time_match.group(1))
            period = time_match.group(2)
            if period == "pm" and hour != 12:
                hour += 12
            elif period == "am" and hour == 12:
                hour = 0
            date = date.replace(hour=hour, minute=0, second=0, microsecond=0)

    return date.strftime("%Y-%m-%d %H:%M:%S")