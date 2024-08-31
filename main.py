import os
from contextlib import contextmanager

import psycopg2
from passlib.handlers.sha2_crypt import sha256_crypt
from fastapi import FastAPI, HTTPException
from psycopg2.extras import RealDictCursor
from starlette.responses import JSONResponse

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

@contextmanager
def get_db_connection():
    connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield connection
    finally:
        connection.close()

@app.get("/")
async def root():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
    return {"database_version": version["version"]}

@app.post("/register")
async def register(email: str, password: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            email = email.replace("%40", "@")
            password_hash = sha256_crypt.hash(password)
            cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Username already exists")

            cursor.execute("INSERT INTO Users (email, password_hash) VALUES (%s, %s)", (email, password_hash))
        conn.commit()
    return JSONResponse(status_code=201, content={"message": "User created successfully"})

@app.post("/login")
async def login(email: str, password: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            email = email.replace("%40", "@")
            cursor.execute("SELECT password_hash FROM Users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user or not sha256_crypt.verify(password, user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid username or password")
    return JSONResponse(status_code=200, content={"message": "Login successful"})

@app.get("/profile")
async def get_user(username: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            result = {
                "username": user["username"],
            }
    return result

seats = set()
MAX_SEATS = 200

@app.post("/seats")
async def select_seat(seat_number: int):
    if len(seats) >= MAX_SEATS:
        raise HTTPException(status_code=400, detail="No more seats available")

    if seat_number < 0 or seat_number >= MAX_SEATS:
        raise HTTPException(status_code=400, detail="Invalid seat number")

    if seat_number in seats:
        raise HTTPException(status_code=400, detail="Seat is already taken")

    seats.add(seat_number)
    return JSONResponse(status_code=200, content={"message": "Seat selected successfully"})

@app.post("/tickets")
async def process_tickets(tickets: list):
    return {"total_seats": len(tickets)}

@app.post("/candy")
async def buy_candy(candy: dict):
    return candy

@app.post("/checkout")
async def checkout():
    return {"message": "Checkout successful"}