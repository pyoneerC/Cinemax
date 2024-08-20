import os
from contextlib import contextmanager

import psycopg2
import requests
from fastapi import FastAPI
from passlib.handlers.sha2_crypt import sha256_crypt
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


@app.post("/login")
async def login(username: str, password: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user:
                if sha256_crypt.verify(password, user["password_hash"]):
                    return JSONResponse(status_code=200, content={"message": "Login successful"})
                else:
                    return JSONResponse(status_code=401, content={"message": "Invalid password"})
    return user

@app.post("/register")
async def register(username: str, password: str, first_name: str = None, last_name: str = None, phone_number: str = None):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:

            password_hash = sha256_crypt.hash(password)

            url = 'https://api.ipgeolocation.io/ipgeo?apiKey=' + os.getenv('IPGEOLOCATION_API_KEY')
            response = requests.get(url)
            data = response.json()

            cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user:
                return JSONResponse(status_code=400, content={"message": "Username already exists"})

            country = data['country_name']
            city = data['city']
            ip = data['ip']
            latitude = data['latitude']
            longitude = data['longitude']

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
                ip,
                latitude,
                longitude,
                country,
                city,
            ))
        conn.commit()
    return JSONResponse(status_code=201, content={"message": "User created successfully"})

@app.get("/profile")
async def get_user(username: str, password: str = None):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
            user = cursor.fetchone()

    if not user:
        return JSONResponse(status_code=404, content={"message": "User not found"})
    else:

        result = {
            "username": user["username"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "profile_picture": user["profile_picture"],
            "phone_number": user["phone_number"],
            "is_email_verified": user["is_email_verified"],
            "country": user["country"],
        }

        return JSONResponse(status_code=200, content=result)