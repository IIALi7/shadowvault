import os
import psycopg2
import time
import uvicorn
from fastapi import FastAPI, HTTPException, Form
from starlette.responses import RedirectResponse

app = FastAPI()

# Ensure DATABASE_URL is set
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL is missing! Set it in Railway.")
    raise Exception("❌ DATABASE_URL is missing! Set it in Railway.")

print(f"🔹 DATABASE_URL found: {DATABASE_URL}")

def get_db_connection():
    """ Attempt to connect to the database with retries to avoid looping errors. """
    retries = 5
    for i in range(retries):
        try:
            print(f"🔹 Attempt {i+1} to connect to the database...")
            conn = psycopg2.connect(DATABASE_URL)
            print("✅ Database connection successful!")
            return conn
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            if i < retries - 1:
                print("🔄 Retrying in 5 seconds...")
                time.sleep(5)
            else:
                raise Exception("❌ Failed to connect to the database after multiple attempts.")

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
    cursor.execute("SELECT role FROM users WHERE username = %s AND password = %s", (username, password))
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

@app.get("/flag")
async def flag():
    return {"flag": "FLAG{shadow_vault_master}"}

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8000))
    print(f"🔹 Starting FastAPI on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
