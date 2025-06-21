from fastapi import APIRouter, Request
from .history_service import load_history, save_history
from .togetherai_service import ask_together_ai

router = APIRouter(prefix="/api")  # Adding the api prefix to all routes

@router.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_message = body.get("message")

    if not user_message:
        return {"error": "No message provided"}

    history = load_history()
    history.append({"role": "user", "content": user_message})

    bot_response = await ask_together_ai(user_message)
    history.append({"role": "assistant", "content": bot_response})

    save_history(history)

    return {"response": bot_response}

@router.get("/history")
async def get_history():
    raw_history = load_history()
    formatted_history = []

    for i in range(0, len(raw_history), 2):
        user_msg = raw_history[i].get("content") if i < len(raw_history) else None
        bot_msg = raw_history[i + 1].get("content") if i + 1 < len(raw_history) else None

        if user_msg is not None and bot_msg is not None:
            formatted_history.append({
                "user": user_msg,
                "bot": bot_msg
            })

    return formatted_history


@router.delete("/history/{index}")
async def delete_history_item(index: int):
    """
    Delete a specific chat history item by its index.
    Args:
        index: The index of the chat history item to delete
    Returns:
        A dictionary with the status of the operation
    """
    # Load the current history
    raw_history = load_history()

    # Check if the index is valid for the formatted history
    formatted_length = len(raw_history) // 2
    if index < 0 or index >= formatted_length:
        return {"status": "error",
                "message": f"Invalid index: {index}. Valid range is 0-{formatted_length - 1 if formatted_length > 0 else 0}"}

    # Calculate the actual indices in the raw history
    user_index = index * 2
    bot_index = user_index + 1

    # Remove both user and bot messages
    if bot_index < len(raw_history):
        # Remove the bot message first (higher index)
        raw_history.pop(bot_index)
    if user_index < len(raw_history):
        # Then remove the user message
        raw_history.pop(user_index)

    # Save the updated history
    save_history(raw_history)

    return {"status": "success", "message": f"History item {index} deleted"}