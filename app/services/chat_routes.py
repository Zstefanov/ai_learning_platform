from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

from .history_service import (
    get_next_conversation_id,
    add_message_to_db,
    delete_history_item,
    load_history_from_db, get_conversation_ids, get_conversation,
)
from .togetherai_service import ask_together_ai

router = APIRouter(prefix="/api")

@router.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_message = body.get("message")
    new_session = body.get("new_session", False)
    convo_index = body.get("convo_index", None)  # This is conversation_id

    if not user_message:
        return {"error": "No message provided"}

    # Start a new conversation if needed
    if new_session or convo_index is None:
        conversation_id = get_next_conversation_id()
    else:
        conversation_id = convo_index

    # Save user message
    add_message_to_db(conversation_id, "user", user_message)

    # Get assistant response and save it
    bot_response = await ask_together_ai(user_message)
    add_message_to_db(conversation_id, "assistant", bot_response)

    return {"response": bot_response, "convo_index": conversation_id}

@router.get("/history")
def get_history():
    conversation_ids = get_conversation_ids()
    result = []
    for cid in conversation_ids:
        messages = get_conversation(cid)
        result.append({
            "conversation_id": cid,
            "messages": messages
        })
    return result

@router.delete("/history/{conversation_id}")
async def delete_history_item_route(conversation_id: int):
    result = delete_history_item(conversation_id)
    return JSONResponse(content=result)