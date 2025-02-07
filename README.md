# Chat Archiver

A **local chat archive program** built with **Python** and **SQLite**, allowing users to **import** and **export** chat messages from **WhatsApp and Twitter**.

## Features
✅ Store chats in a local **SQLite database**.  
✅ Import chats from **WhatsApp (TXT format)** and **Twitter (JSON format)**.  
✅ Export chat history as a **responsive HTML file**.  
✅ **Color-coded chat messages** to indicate different sources (WhatsApp/Twitter).  

## Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/chat-archiver.git
   cd chat-archiver
   ```
2. **Run the program:**
   ```sh
   python main.py
   ```

## Usage

### 📥 Importing Chats
1. Select `Import Chat` from the menu.
2. Choose between:
   - **WhatsApp (1)**: Requires **sender name, receiver name, and TXT file path**.
   - **Twitter (2)**: Requires **sender ID, receiver ID, and JSON file path**.
3. The chat will be stored in the database.

### 📤 Exporting Chats
1. Select `Export Chat` from the menu.
2. Choose a **user ID** to export their chat.
3. The chat will be saved as an **HTML file** with proper formatting.

---

## 📄 Chat Templates

### **WhatsApp Chat Format (`input.txt`)**
```
01/01/24, 7:57 AM - sender: Good morning! Have a great day! ☀️
01/01/24, 7:58 AM - receiver: Thanks! You too 😊
```
📌 **Notes:**  
- Messages **can span multiple lines**.  
- Each message starts with a **timestamp**, followed by the **sender**, and the **message content**.  

---

### **Twitter Chat Format (`input.json`)**
```json
{
  "dmConversation": {
    "conversationId": "recipientId-senderId",
    "messages": [
      {
        "messageCreate": {
          "recipientId": "recipientId",
          "text": "Good morning! Have a great day! ☀️",
          "senderId": "senderId",
          "createdAt": "2024-01-01T07:57:20.538Z"
        }
      },
      {
        "messageCreate": {
          "recipientId": "senderId",
          "text": "Thanks! You too 😊",
          "senderId": "recipientId",
          "createdAt": "2024-01-01T07:58:20.538Z"
        }
      }
    ]
  }
}
```
📌 **Notes:**  
- Messages are stored in **JSON format** under `"messages"` list.  
- `"senderId"` and `"recipientId"` indicate who sent/received the message.  
- `"createdAt"` contains the **timestamp** (converted to standard format in the database).  

---

## 📂 Project Structure
```
chat-archiver/
│-- chat_archive.db    # SQLite database (auto-created)
│-- main.py            # Main script
│-- README.md          # Documentation
```

## 💡 Future Improvements
- Add support for **Telegram** and other chat sources.
- Implement a **search feature** for archived chats.
- Build a **simple UI** for better interaction.

## 🤝 Contributing
Feel free to **fork** this repository, submit **issues**, or create **pull requests**! 🚀

---

### 📜 License
This project is **open-source** and free to use! 📖
