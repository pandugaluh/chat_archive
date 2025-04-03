import sqlite3
import os
import datetime
import json

def init_db():
    """Initialize the database and create tables if not exists."""
    conn = sqlite3.connect("chat_archive.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    chat_role TEXT,
                    message TEXT,
                    timestamp TEXT,
                    source TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                 )''')
    conn.commit()
    conn.close()

def message_exists(user_id, chat_role, timestamp):
    """Check if a message already exists in the database."""
    conn = sqlite3.connect("chat_archive.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM chats WHERE user_id = ? AND chat_role = ? AND timestamp = ?", (user_id, chat_role, timestamp))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def format_date(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %d %B %Y")

def format_time(time_str):
    return datetime.datetime.strptime(time_str, "%H:%M:%S").strftime("%H:%M")

def import_chat():
    """Prompt user to select a chat import source."""
    print("Select import source:")
    print("1. WhatsApp")
    print("2. Twitter")
    choice = input("Enter your choice: ")
    
    if choice == "1":
        import_whatsapp_chat()
    elif choice == "2":
        import_twitter_chat()
    else:
        print("Invalid choice.")

def import_whatsapp_chat():
    """Import WhatsApp chat messages."""
    user_id = get_user_id()
    sender = input("Enter sender name: ")
    receiver = input("Enter receiver name: ")
    file_path = get_file_path()
    import_whatsapp(file_path, sender, receiver, user_id, "whatsapp")

def import_twitter_chat():
    """Import Twitter chat messages."""
    user_id = get_user_id()
    sender_id = input("Enter sender ID: ")
    receiver_id = input("Enter receiver ID: ")
    file_path = get_file_path()
    import_twitter(file_path, sender_id, receiver_id, user_id, "twitter")

def get_user_id():
    """Retrieve user ID from database, create if not exists."""
    user_name = input("Enter your user ID (name): ")
    conn = sqlite3.connect("chat_archive.db")
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE name = ?", (user_name,))
    user = c.fetchone()
    if user:
        user_id = user[0]
    else:
        c.execute("INSERT INTO users (name) VALUES (?)", (user_name,))
        user_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_file_path():
    """Prompt user to enter file path."""
    file_path = input("Enter full path of input.txt (or just input.txt if in the same directory): ")
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getcwd(), file_path)
    return file_path

def import_whatsapp(file_path, sender, receiver, user_id, source):
    """Process and import WhatsApp messages from a text file."""
    try:
        conn = sqlite3.connect("chat_archive.db")
        c = conn.cursor()
        
        with open(file_path, "r", encoding="utf-8") as file:
            message_buffer = []
            timestamp = None
            chat_role = None
            
            for line in file:
                parts = line.strip().split(" - ", 1)
                if len(parts) == 2:
                    if message_buffer:
                        if not message_exists(user_id, chat_role, timestamp):
                            c.execute("INSERT INTO chats (user_id, chat_role, message, timestamp, source) VALUES (?, ?, ?, ?, ?)",
                                    (user_id, chat_role, "\n".join(message_buffer), timestamp, source))
                            print(f"Imported: {chat_role}: {' '.join(message_buffer)}")
                        message_buffer = []
                    timestamp = datetime.datetime.strptime(parts[0], "%m/%d/%y, %I:%M %p").strftime("%Y-%m-%d %H:%M:%S")
                    sender_message = parts[1].split(": ", 1)
                    if len(sender_message) == 2:
                        detected_sender, message = sender_message
                        chat_role = "sender" if detected_sender == sender else "receiver"
                        message_buffer.append(message)
                else:
                    message_buffer.append(line.strip())
            
            if message_buffer and not message_exists(user_id, chat_role, timestamp):
                c.execute("INSERT INTO chats (user_id, chat_role, message, timestamp, source) VALUES (?, ?, ?, ?, ?)",
                          (user_id, chat_role, "\n".join(message_buffer), timestamp, source))
                print(f"Imported: {chat_role}: {' '.join(message_buffer)}")
        
        conn.commit()
        conn.close()
        print("WhatsApp chat imported successfully!")
    except Exception as e:
        print("Error importing chat:", e)

def import_twitter(file_path, sender_id, receiver_id, user_id, source):
    try:
        conn = sqlite3.connect("chat_archive.db")
        c = conn.cursor()
        
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            messages = data.get("dmConversation", {}).get("messages", [])
            
            for message_data in messages:
                message_obj = message_data.get("messageCreate", {})
                message_text = message_obj.get("text", "")
                message_timestamp = message_obj.get("createdAt", "")
                message_sender = message_obj.get("senderId", "")
                
                timestamp = datetime.datetime.strptime(message_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
                chat_role = "sender" if message_sender == sender_id else "receiver"
                
                c.execute("INSERT INTO chats (user_id, chat_role, message, timestamp, source) VALUES (?, ?, ?, ?, ?)",
                          (user_id, chat_role, message_text, timestamp, source))
                print(f"Imported: {chat_role}: {message_text}")
        
        conn.commit()
        conn.close()
        print("Twitter chat imported successfully!")
    except Exception as e:
        print("Error importing chat:", e)

def delete_chat():
    """Delete all messages and the user from the database."""
    conn = sqlite3.connect("chat_archive.db")
    c = conn.cursor()
    c.execute("SELECT id, name FROM users")
    users = c.fetchall()

    if not users:
        print("No users found.")
        return
    
    print("Select user to delete chat:")
    for user in users:
        print(f"{user[0]}. {user[1]}")

    user_id = input("Enter user ID to delete chat and user: ")
    
    # Check if user exists before deletion
    c.execute("SELECT name FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    
    if not user:
        print("User not found.")
        conn.close()
        return
    
    # Delete chats of the selected user
    c.execute("DELETE FROM chats WHERE user_id = ?", (user_id,))
    
    # Delete the user from the users table
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    
    conn.commit()
    conn.close()

    print(f"Deleted all messages and removed user '{user[0]}' (ID {user_id}) successfully!")

def check_duplicate():
    """Check and remove duplicate messages for a selected user."""
    conn = sqlite3.connect("chat_archive.db")
    c = conn.cursor()
    c.execute("SELECT id, name FROM users")
    users = c.fetchall()
    
    if not users:
        print("No users found.")
        return
    
    print("Select user to check for duplicate messages:")
    for user in users:
        print(f"{user[0]}. {user[1]}")
    
    user_id = input("Enter user ID to check for duplicates: ")
    
    c.execute("""DELETE FROM chats 
                 WHERE id NOT IN (
                     SELECT MIN(id) 
                     FROM chats 
                     WHERE user_id = ?
                     GROUP BY chat_role, message, timestamp
                 )""", (user_id,))
    
    conn.commit()
    conn.close()
    
    print(f"Removed duplicate messages for user ID {user_id}")

def export_chat():
    conn = sqlite3.connect("chat_archive.db")
    c = conn.cursor()
    c.execute("SELECT id, name FROM users")
    users = c.fetchall()
    conn.close()
    
    print("Select user to export chat:")
    for user in users:
        print(f"{user[0]}. {user[1]}")
    user_id = input("Enter user ID: ")
    
    conn = sqlite3.connect("chat_archive.db")
    c = conn.cursor()
    c.execute("SELECT name FROM users WHERE id = ?", (user_id,))
    user_name = c.fetchone()[0]
    c.execute("SELECT message, timestamp, chat_role, source FROM chats WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
    chats = c.fetchall()
    conn.close()
    
    output_file = f"chat_export_{user_id}.html"
    html_content = f"""
    <html>
    <head>
        <title>Chat Archive</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 10px;
                background-color: #f5f5f5;
            }}
            .day-header {{
                font-weight: bold;
                text-align: center;
                margin-top: 20px;
                color: #333;
            }}
            .chat-container {{
                max-width: 600px;
                margin: auto;
                padding: 10px;
            }}
            .chat-block {{
                display: flex;
                flex-direction: column;
                margin: 10px 0;
                padding: 10px;
                border-radius: 8px;
                max-width: 100%;
                word-wrap: break-word;
                white-space: pre-wrap;
                overflow-wrap: break-word;
            }}
            .whatsapp-sender {{
                background-color: #a5d6a7;
            }}
            .whatsapp-receiver {{
                background-color: #dcf8c6;
            }}
            .twitter-sender {{
                background-color: #90caf9;
            }}
            .twitter-receiver {{
                background-color: #e8f5fd;
            }}
            .left {{
                align-self: flex-start;
            }}
            .right {{
                align-self: flex-end;
                text-align: right;
            }}
            .timestamp {{
                font-size: small;
                color: gray;
                margin-bottom: 5px;
            }}
            .chat {{
                padding: 8px;
                border-radius: 8px;
                max-width: 100%;
                word-wrap: break-word;
                white-space: pre-wrap;
                overflow-wrap: break-word;
            }}
        </style>
    </head>
    <body>
        <h2 style="text-align: center;">Chat Archive for {user_name}</h2>
        <div class="chat-container">
    """
    
    last_date = None
    for message, timestamp, chat_role, source in chats:
        date, time = timestamp.split(" ")[0], timestamp.split(" ")[1]
        formatted_date = format_date(date)
        formatted_time = format_time(time)
        
        if date != last_date:
            html_content += f'<div class="day-header">{formatted_date}</div>'
            last_date = date
        
        align_class = "right" if chat_role == "sender" else "left"
        source_class = f"{source}-sender" if chat_role == "sender" else f"{source}-receiver"
        
        html_content += f'''
        <div class="chat-block {align_class} {source_class}">
            <span class="timestamp">{formatted_time}</span>
            <div class="chat">{message}</div>
        </div>
        '''
    
    html_content += "</div></body></html>"
    
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print(f"Chat exported successfully to {output_file}!")

def main():
    """Main menu for chat manager."""
    init_db()
    while True:
        print("Select an option:")
        print("1. Import Chat")
        print("2. Export Chat")
        print("3. Delete Chat by User ID")
        print("4. Check & Remove Duplicate Messages")
        print("5. Exit")

        choice = input("Enter your choice: ")
        
        if choice == "1":
            import_chat()
        elif choice == "2":
            export_chat()
        elif choice == "3":
            delete_chat()
        elif choice == "4":
            check_duplicate()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()