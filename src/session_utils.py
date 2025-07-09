session_chats = {}

def get_chat_history(session_id):
    return session_chats.get(session_id, [])

def add_chat_to_history(session_id, question, answer):
    if session_id not in session_chats:
        session_chats[session_id] = []
    session_chats[session_id].append((question, answer))

def clear_chat_history():
    global session_chats
    session_chats = {}
