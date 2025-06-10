
session_memory = {}

def get_session_state(user_id):
    if user_id not in session_memory:
        session_memory[user_id] = {
            "mode": None,
            "pending_coin": None,
            "portfolio": {}
        }
    return session_memory[user_id]