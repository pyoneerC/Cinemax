import os
from contextlib import contextmanager

import psycopg2
from passlib.handlers.sha2_crypt import sha256_crypt
from fastapi import FastAPI, HTTPException
from psycopg2.extras import RealDictCursor
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
                raise HTTPException(status_code=400, detail="Email already exists")

            cursor.execute("INSERT INTO Users (email, password_hash) VALUES (%s, %s)", (email, password_hash))
        conn.commit()
    return JSONResponse(status_code=201, content={"message": "User created successfully"})

@app.post("/login")
async def login(email: str, password: str, movie: str, time: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            email = email.replace("%40", "@")

            cursor.execute("SELECT id, password_hash FROM Users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user or not sha256_crypt.verify(password, user["password_hash"]):
                raise HTTPException(status_code=401, detail="Incorrect email or password")

            user_id = user["id"]

            cursor.execute(
                """
                INSERT INTO Reservations (user_id, email, movie, reservation_time)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, email, movie, time)
            )
            conn.commit()

    return JSONResponse(status_code=200, content={"message": True})

@app.put("/reset")
async def reset_password(email: str, password: str, new_password: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            email = email.replace("%40", "@")

            cursor.execute("SELECT password_hash FROM Users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user or not sha256_crypt.verify(password, user["password_hash"]):
                raise HTTPException(status_code=404, detail="User not found or incorrect password")

            new_password_hash = sha256_crypt.hash(new_password)
            cursor.execute("UPDATE Users SET password_hash = %s WHERE email = %s", (new_password_hash, email))

        conn.commit()
        return JSONResponse(status_code=200, content={"message": "Password reset successfully"})

@app.get("/profile")
async def get_user(email: str, password: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT password_hash,email,created_at,id FROM Users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user or not sha256_crypt.verify(password, user["password_hash"]):
                raise HTTPException(status_code=404, detail="User not found")
            response= {
                'email': user['email'],
                'created_at': user['created_at'],
                'id': user['id']
            }
    return response


@app.post("/profile")
async def update_user(email: str, password: str, username: str = None, first_name: str = None,
                      last_name: str = None, phone_number: str = None, is_email_verified: bool = False):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT password_hash FROM Users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user or not sha256_crypt.verify(password, user["password_hash"]):
                raise HTTPException(status_code=404, detail="User not found or incorrect password")

            cursor.execute("""
                UPDATE Users
                SET username = COALESCE(%s, username),
                    first_name = COALESCE(%s, first_name),
                    last_name = COALESCE(%s, last_name),
                    phone_number = COALESCE(%s, phone_number),
                    is_email_verified = %s
                WHERE email = %s
            """, (username, first_name, last_name, phone_number, is_email_verified, email))
            conn.commit()

    return JSONResponse(status_code=200, content={"message": "Profile updated successfully"})

@app.post("/tickets")
async def insert_tickets(num: int):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO reservations (tickets) VALUES (%s)", (num,))
        conn.commit()
    return JSONResponse(status_code=201, content={"message": True})