import csv
import sqlite3

conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()

query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
cursor.execute(query)
query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
cursor.execute(query)

# Create tables for new features
# Weather preferences table
query = "CREATE TABLE IF NOT EXISTS weather_preferences(id integer primary key, default_location VARCHAR(100), units VARCHAR(10) DEFAULT 'metric')"
cursor.execute(query)

# Weather search history
query = "CREATE TABLE IF NOT EXISTS weather_search_history(id integer primary key, location VARCHAR(100), search_date TEXT DEFAULT CURRENT_TIMESTAMP)"
cursor.execute(query)

# Calendar events table
query = "CREATE TABLE IF NOT EXISTS events(id integer primary key, title TEXT NOT NULL, datetime TEXT NOT NULL, description TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)"
cursor.execute(query)

# Reminders table
query = "CREATE TABLE IF NOT EXISTS reminders(id integer primary key, message TEXT NOT NULL, trigger_time TEXT NOT NULL, is_active INTEGER DEFAULT 1)"
cursor.execute(query)

# Notes table
query = "CREATE TABLE IF NOT EXISTS notes(id integer primary key, content TEXT NOT NULL, category TEXT, tags TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)"
cursor.execute(query)

# Commit the changes
conn.commit()


# query = "INSERT INTO sys_command VALUES (null,'obs', 'C:\\Program Files\\obs-studio\\bin\\obs64.exe')"
# cursor.execute(query)
# conn.commit()

# query = "DELETE FROM sys_command WHERE name='obs'"
# cursor.execute(query)
# conn.commit()

# testing module
# app_name = "obs"
# cursor.execute('SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
# results = cursor.fetchall()
# print(results[0][0])




# cursor.execute("DROP TABLE IF EXISTS contacts;")
# conn.commit()
# cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, name VARCHAR(200), Phone VARCHAR(255), email VARCHAR(255) NULL)''') 

 
# desired_columns_indices = [0, 20]
 
# with open('contacts.csv', 'r', encoding='utf-8') as csvfile:
#     csvreader = csv.reader(csvfile)
#     for row in csvreader:
#         selected_data = [row[i] for i in desired_columns_indices]
#         cursor.execute(''' INSERT INTO contacts (id, 'name', 'Phone') VALUES (null, ?,? );''', tuple(selected_data))

# # Commit changes and close connection
# conn.commit()
# conn.close()

# print("Data inserted successfully") 


# query = "INSERT INTO contacts VALUES (null,'pawan', '1234567890', 'null')"
# cursor.execute(query)
# conn.commit() 


# query = 'Ankit'
# query = query.strip().lower()  # Added parentheses to call the method

# cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", 
#                ('%' + query + '%', query + '%'))
# results = cursor.fetchall()
# print(results[0][0])
