import sqlite3
import os
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse
from passlib.hash import bcrypt

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


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "db", "my_database.db")


@router.post("/register")
def register_user(req: RegisterRequest):
    hashed_pw = bcrypt.hash(req.password)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (req.username, req.email, hashed_pw)
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=400, detail="Username or email already exists.")
    conn.close()
    return {"status": "success", "message": "User registered successfully."}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
def login_user(req: LoginRequest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash FROM users WHERE email = ?", (req.email,)
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    password_hash = row[0]
    if not bcrypt.verify(req.password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"status": "success", "message": "Login successful"}


class DeleteAccountRequest(BaseModel):
    email: EmailStr
    password: str

@router.delete("/delete-account")
def delete_account(req: DeleteAccountRequest):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash FROM users WHERE email = ?", (req.email,)
    )
    row = cursor.fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid email or password")
    password_hash = row[0]
    if not bcrypt.verify(req.password, password_hash):
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid email or password")
    cursor.execute(
        "DELETE FROM users WHERE email = ?", (req.email,)
    )
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Account deleted successfully."}