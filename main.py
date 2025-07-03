from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.services.chat_routes import router as chat_router
import os

app = FastAPI()

# Enable frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include chat API
app.include_router(chat_router)
print("Registered routes:")
for route in app.routes:
    print(route.path)

# Serve frontend files
app.mount(
    path="/",
    app=StaticFiles(directory=os.path.join(os.path.dirname(__file__), "app/frontend"), html=True),
    name="frontend"
)