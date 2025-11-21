import sqlite3
import datetime
import eel
from backend.command import speak

conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()

# Note-taking Functions
@eel.expose
def saveNote(content, category="general"):
    """Save note with automatic categorization"""
    try:
        # Auto-categorize based on content
        if category == "general":
            category = categorizeNote(content)

        # Extract tags from content
        tags = extractTags(content)
        tags_str = ", ".join(tags) if tags else ""

        cursor.execute("INSERT INTO notes (content, category, tags) VALUES (?, ?, ?)",
                      (content, category, tags_str))
        conn.commit()

        speak(f"Note saved under category: {category}")
        return {"success": True, "message": f"Note saved as {category}"}

    except Exception as e:
        print(f"Error saving note: {e}")
        speak("Sorry, I couldn't save your note.")
        return {"success": False, "error": str(e)}

@eel.expose
def searchNotes(query):
    """Search notes by content or category"""
    try:
        search_term = f"%{query}%"
        cursor.execute("""
            SELECT id, content, category, tags, created_at, updated_at
            FROM notes
            WHERE content LIKE ? OR category LIKE ? OR tags LIKE ?
            ORDER BY created_at DESC
        """, (search_term, search_term, search_term))

        notes = cursor.fetchall()
        note_list = []

        for note in notes:
            created_date = datetime.datetime.strptime(note[4], "%Y-%m-%d %H:%M:%S")
            note_list.append({
                'id': note[0],
                'content': note[1],
                'category': note[2],
                'tags': note[3].split(", ") if note[3] else [],
                'created_at': created_date.strftime("%B %d, %Y at %I:%M %p"),
                'updated_at': note[5]
            })

        if note_list:
            speak(f"Found {len(note_list)} notes matching '{query}'")
        else:
            speak(f"No notes found matching '{query}'")

        return {"success": True, "notes": note_list}

    except Exception as e:
        print(f"Error searching notes: {e}")
        speak("Sorry, I couldn't search your notes.")
        return {"success": False, "error": str(e)}

@eel.expose
def getRecentNotes(count=10):
    """Retrieve recent notes"""
    try:
        cursor.execute("""
            SELECT id, content, category, tags, created_at
            FROM notes
            ORDER BY created_at DESC
            LIMIT ?
        """, (count,))

        notes = cursor.fetchall()
        note_list = []

        for note in notes:
            created_date = datetime.datetime.strptime(note[4], "%Y-%m-%d %H:%M:%S")
            note_list.append({
                'id': note[0],
                'content': note[1][:100] + "..." if len(note[1]) > 100 else note[1],
                'category': note[2],
                'tags': note[3].split(", ") if note[3] else [],
                'created_at': created_date.strftime("%B %d, %Y")
            })

        if note_list:
            speak(f"Here are your {len(note_list)} most recent notes")
        else:
            speak("You don't have any notes yet")

        # Display notes in frontend
        eel.displayNotes({"success": True, "notes": note_list})

        return {"success": True, "notes": note_list}

    except Exception as e:
        print(f"Error getting recent notes: {e}")
        speak("Sorry, I couldn't retrieve your recent notes.")
        return {"success": False, "error": str(e)}

@eel.expose
def deleteNote(note_id):
    """Delete a note by ID"""
    try:
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()

        if cursor.rowcount > 0:
            speak("Note deleted successfully")
            return {"success": True, "message": "Note deleted"}
        else:
            speak("Note not found")
            return {"success": False, "message": "Note not found"}

    except Exception as e:
        print(f"Error deleting note: {e}")
        speak("Sorry, I couldn't delete that note.")
        return {"success": False, "error": str(e)}

def categorizeNote(content):
    """Automatically categorize note based on content"""
    content_lower = content.lower()

    # Simple keyword-based categorization
    categories = {
        "work": ["meeting", "project", "deadline", "work", "office", "client", "task"],
        "personal": ["personal", "family", "friend", "home", "private"],
        "shopping": ["buy", "purchase", "shopping", "store", "market", "grocery"],
        "ideas": ["idea", "thought", "inspiration", "concept", "creative"],
        "health": ["health", "exercise", "workout", "medicine", "doctor", "appointment"],
        "travel": ["travel", "trip", "vacation", "hotel", "flight", "destination"],
        "finance": ["money", "budget", "expense", "income", "bill", "payment"],
        "learning": ["learn", "study", "course", "book", "tutorial", "education"]
    }

    for category, keywords in categories.items():
        if any(keyword in content_lower for keyword in keywords):
            return category

    return "general"

def extractTags(content):
    """Extract potential tags from note content"""
    import re

    # Simple hashtag extraction
    hashtags = re.findall(r'#(\w+)', content)

    # Simple @mention extraction
    mentions = re.findall(r'@(\w+)', content)

    return hashtags + mentions

def processNoteCommand(query):
    """Process note-taking voice commands"""
    query_lower = query.lower()

    if any(phrase in query_lower for phrase in ["take a note", "save note", "remember this", "make a note"]):
        # Extract content after the trigger phrase
        content = extractNoteContent(query)

        if content:
            # Determine category from query
            category = extractCategoryFromQuery(query)
            saveNote(content, category)
        else:
            speak("What would you like me to note down?")
            # In a real implementation, you'd wait for voice input here
        return True

    elif "search notes" in query_lower or "find notes" in query_lower:
        search_term = extractSearchTerm(query)
        if search_term:
            searchNotes(search_term)
        else:
            speak("What would you like me to search for in your notes?")
        return True

    elif "recent notes" in query_lower or "show notes" in query_lower:
        getRecentNotes()
        return True

    return False

def extractNoteContent(query):
    """Extract the actual note content from voice command"""
    triggers = ["take a note", "save note", "remember this", "make a note", "note that"]

    for trigger in triggers:
        if trigger in query_lower:
            content = query_lower.replace(trigger, "").strip()
            # Remove common filler words
            content = content.replace("please", "").replace("can you", "").replace("could you", "")
            return content if content else None

    return None

def extractCategoryFromQuery(query):
    """Extract category from note command"""
    query_lower = query.lower()

    if "work" in query_lower:
        return "work"
    elif "personal" in query_lower:
        return "personal"
    elif "shopping" in query_lower:
        return "shopping"
    elif "idea" in query_lower or "ideas" in query_lower:
        return "ideas"
    elif "health" in query_lower:
        return "health"
    elif "travel" in query_lower:
        return "travel"
    elif "finance" in query_lower or "money" in query_lower:
        return "finance"
    elif "learn" in query_lower or "study" in query_lower:
        return "learning"

    return "general"

def extractSearchTerm(query):
    """Extract search term from search command"""
    triggers = ["search notes for", "find notes about", "search for", "find"]

    for trigger in triggers:
        if trigger in query_lower:
            term = query_lower.replace(trigger, "").strip()
            return term if term else None

    return None