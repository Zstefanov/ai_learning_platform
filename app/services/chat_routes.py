from fastapi import APIRouter, Request
from .history_service import load_history, save_history, load_history_from_db
from .togetherai_service import ask_together_ai
import os

router = APIRouter(prefix="/api")

@router.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_message = body.get("message")
    new_session = body.get("new_session", False)
    convo_index = body.get("convo_index", None)

    if not user_message:
        return {"error": "No message provided"}

    history = load_history()

    if not history or new_session:
        history.append([])  # start a new conversation list if empty or new session requested
        convo_index = len(history) - 1 #index of the new conversation

    elif convo_index is not None and 0 <= convo_index < len(history):
        pass
    else:
        current_convo = history[-1]

    current_convo = history[convo_index]
    current_convo.append({"role": "user", "content": user_message})

    bot_response = await ask_together_ai(user_message)
    current_convo.append({"role": "assistant", "content": bot_response})

    save_history(history)

    return {"response": bot_response, "convo_index": convo_index}

@router.get("/history")
async def get_history():
    # /old implementation/ Return raw chat history JSON (list of conversations) - refactored to use DB
    # return load_history()
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, "db", "my_database.db")
    return load_history_from_db(db_path)


@router.delete("/history/{index}")
async def delete_history_item(index: int):
    history = load_history()

    if index < 0 or index >= len(history):
        return {"status": "error", "message": f"Invalid index: {index}"}

    history.pop(index)
    save_history(history)

    return {"status": "success", "message": f"Conversation {index} deleted"}
