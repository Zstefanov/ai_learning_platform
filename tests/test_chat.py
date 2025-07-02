import sqlite3
import pytest
import uuid

#Sends a chat message to the /api/chat endpoint and checks if it is saved in the history table
@pytest.mark.asyncio
async def test_chat_message_saved(async_client, db_path):
    unique_id = uuid.uuid4().hex[:6]
    test_message = f"Hello, this is a real test message {unique_id}"

    # Post to /api/chat to start a new conversation
    chat_payload = {
        "message": test_message,
        "new_session": True
    }
    response = await async_client.post("/api/chat", json=chat_payload)
    print(f"Chat response status: {response.status_code}")
    print(f"Chat response content: {await response.aread()}")
    assert response.status_code == 200

    resp_json = response.json()
    conversation_id = resp_json.get("convo_index")
    assert conversation_id is not None, "No conversation_id returned"
    bot_response = resp_json.get("response")
    assert bot_response and isinstance(bot_response, str) and len(bot_response) > 0

    # Check that history table has both user and assistant messages for this conversation
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM history WHERE conversation_id = ? ORDER BY id ASC",
        (conversation_id,)
    )
    messages = cursor.fetchall()
    conn.close()

    # Expect 2 messages: user then assistant
    assert len(messages) == 2, f"Expected 2 messages, got {len(messages)}"
    assert messages[0][0] == "user"
    assert test_message in messages[0][1]
    assert messages[1][0] == "assistant"
    assert bot_response in messages[1][1]

    print(f"Chat saved in DB for conversation_id {conversation_id}: {messages}")

    # Cleanup: remove test history
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history WHERE conversation_id = ?", (conversation_id,))
    conn.commit()
    conn.close()