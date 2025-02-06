import sqlite3
import os
import datetime

def init_db():
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
                    FOREIGN KEY (user_id) REFERENCES users(id)
                 )''')
    conn.commit()
    conn.close()

def format_date(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %d %B %Y")

def format_time(time_str):
    return datetime.datetime.strptime(time_str, "%H:%M:%S").strftime("%H:%M")

def import_chat():
    print("Select import source:")
    print("1. WhatsApp")
    print("2. Twitter")
    choice = input("Enter your choice: ")
    
    if choice == "1":
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
        
        sender = input("Enter sender name: ")
        receiver = input("Enter receiver name: ")
        file_path = input("Enter full path of input.txt (or just input.txt if in the same directory): ")
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)
        import_whatsapp(file_path, sender, receiver, user_id)
    elif choice == "2":
        print("Twitter import not available now.")
    else:
        print("Invalid choice.")

def import_whatsapp(file_path, sender, receiver, user_id):
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
                        c.execute("INSERT INTO chats (user_id, chat_role, message, timestamp) VALUES (?, ?, ?, ?)",
                                  (user_id, chat_role, "\n".join(message_buffer), timestamp))
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
            
            if message_buffer:
                c.execute("INSERT INTO chats (user_id, chat_role, message, timestamp) VALUES (?, ?, ?, ?)",
                          (user_id, chat_role, "\n".join(message_buffer), timestamp))
                print(f"Imported: {chat_role}: {' '.join(message_buffer)}")
        
        conn.commit()
        conn.close()
        print("WhatsApp chat imported successfully!")
    except Exception as e:
        print("Error importing chat:", e)

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
    c.execute("SELECT message, timestamp, chat_role FROM chats WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
    chats = c.fetchall()
    conn.close()
    
    output_file = f"chat_export_{user_id}.html"
    html_content = f"""
    <html>
    <head>
        <title>Chat Archive</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 10px; }}
            .day-header {{ font-weight: bold; text-align: center; margin-top: 20px; }}
            .chat-container {{ max-width: 600px; margin: auto; }}
            .chat-block {{ display: flex; flex-direction: column; margin: 10px 0; padding: 5px; border-radius: 8px; max-width: 80%; }}
            .left {{ background-color: #f1f0f0; align-self: flex-start; }}
            .right {{ background-color: #dcf8c6; align-self: flex-end; text-align: right; }}
            .timestamp {{ font-size: small; color: gray; margin-bottom: 5px; }}
        </style>
    </head>
    <body>
        <h2 style="text-align: center;">Chat Archive for {user_name}</h2>
        <div class="chat-container">
    """
    
    last_date = None
    for message, timestamp, chat_role in chats:
        date, time = timestamp.split(" ")[0], timestamp.split(" ")[1]
        formatted_date = format_date(date)
        formatted_time = format_time(time)
        if date != last_date:
            html_content += f'<div class="day-header">{formatted_date}</div>'
            last_date = date
        align_class = "right" if chat_role == "sender" else "left"
        html_content += f'<div class="chat-block {align_class}"><span class="timestamp">{formatted_time}</span><div class="chat">{message}</div></div>'
    
    html_content += "</div></body></html>"
    
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print(f"Chat exported successfully to {output_file}!")

def main():
    init_db()
    while True:
        print("Select an option:")
        print("1. Import Chat")
        print("2. Export Chat")
        print("3. Exit")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            import_chat()
        elif choice == "2":
            export_chat()
        elif choice == "3":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()