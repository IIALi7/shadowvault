import os
import psycopg2
from fastapi import FastAPI, Request, Form, HTTPException
from starlette.responses import RedirectResponse

app = FastAPI()

# Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Initialize Database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'supersecurepassword', 'admin') ON CONFLICT DO NOTHING")
    cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guestpass', 'user') ON CONFLICT DO NOTHING")
    conn.commit()
    conn.close()

init_db()

@app.get("/")
async def home():
    return {"message": "Welcome to Shadow Vault. Login to access the system."}

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = f"SELECT role FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()

    if result:
        role = result[0]
        if role == "admin":
            return RedirectResponse(url="/admin", status_code=302)
        return {"message": "Login successful. But you are not an admin!"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/admin")
async def admin_panel():
    return {"message": "Welcome to the Shadow Vault Admin Panel. But where's the flag?"}

@app.get("/api/avatar")
async def fetch_avatar(url: str):
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    return {"avatar": f"Fetching {url}"}

@app.get("/flag")
async def flag():
    return {"flag": "D4rk{shadow_vault_master}"}

import os
import uvicorn
from fastapi import FastAPI

app = FastAPI()

# Get Railway's dynamically assigned port (default to 8000 if not set)
PORT = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("❌ DATABASE_URL is missing! Make sure it's set in Railway.")

def get_db_connection():
    try:
        print(f"🔹 Connecting to: {DATABASE_URL}")  # Debug print
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        raise Exception(f"❌ Database connection failed: {e}")

