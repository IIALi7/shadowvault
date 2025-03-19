from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
import sqlite3
from starlette.responses import HTMLResponse, JSONResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# Home Page
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Login Page
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Vulnerable Login Route
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect("shadowvault.db")
    cursor = conn.cursor()

    # 🚨 **Vulnerable to SQL Injection!** 🚨
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)

    user = cursor.fetchone()
    conn.close()

    if user:
        return JSONResponse({"message": "Login successful", "flag": "D4rk{shadow_vault_master}"})
    else:
        return JSONResponse({"detail": "Invalid username or password."})
