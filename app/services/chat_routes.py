from fastapi import APIRouter, Request
from .history_service import load_history, save_history
from .togetherai_service import ask_together_ai

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
    # Return raw chat history (list of conversations)
    return load_history()

@router.delete("/history/{index}")
async def delete_history_item(index: int):
    history = load_history()

    if index < 0 or index >= len(history):
        return {"status": "error", "message": f"Invalid index: {index}"}

    history.pop(index)
    save_history(history)

    return {"status": "success", "message": f"Conversation {index} deleted"}
