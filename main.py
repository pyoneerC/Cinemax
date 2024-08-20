import os
from fastapi import FastAPI, Depends
import psycopg2
from passlib.handlers.sha2_crypt import sha256_crypt
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

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


@app.post("/login")
async def login(username: str, password: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password_hash = %s", (username, password))
            user = cursor.fetchone()
    return user

@app.post("/register")
async def register(username: str, password: str, first_name: str = None, last_name: str = None, phone_number: str = None, country: str = None, city: str = None):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            password_hash = sha256_crypt.hash(password)
            cursor.execute("""
                INSERT INTO Users (
                    username, email, password_hash, first_name, last_name, profile_picture,
                    phone_number, is_email_verified, is_active, last_login, ip_address,
                    latitude, longitude, country, city
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                username,
                f"{username}@example.com",
                password_hash,
                first_name,
                last_name,
                'https://placehold.jp/200x200.png',
                phone_number,
                False,
                True,
                '2024-08-19 10:00:00',
                '192.168.1.1',
                40.7128,
                -74.0060,
                country,
                city,
            ))
        conn.commit()
    return {"status": "success"}

