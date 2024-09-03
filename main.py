import uuid
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

            transaction_id = 'TX_' + uuid.uuid4().hex[:9].upper()
            order_id = 'ORD_' + uuid.uuid4().hex[:9].upper()

            cursor.execute(
                """
                INSERT INTO Reservations (user_id, email, movie, reservation_time, transaction_id, order_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (user_id, email, movie, time, transaction_id, order_id)
            )
            conn.commit()

            response = {"message": True,
                        "transaction_id": transaction_id,
                        "order_id": order_id}

    return response

@app.post("/tickets")
async def insert_tickets(num: int, price: int, transaction_id: str, order_id: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE Reservations
                SET tickets = %s, price = %s
                WHERE transaction_id = %s AND order_id = %s
                """,
                (num, price, transaction_id, order_id)
            )
        conn.commit()
    return JSONResponse(status_code=201, content={"message": True})

@app.post("/seats")
async def insert_seats(seats: str, transaction_id: str, order_id: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE Reservations SET seats = %s WHERE transaction_id = %s AND order_id = %s", (seats, transaction_id, order_id))
        conn.commit()
    return JSONResponse(status_code=201, content={"message": True})

@app.get("/reservation-details")
async def get_reservation_details(transaction_id: str, order_id: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Reservations WHERE transaction_id = %s AND order_id = %s", (transaction_id, order_id))
            reservation = cursor.fetchone()
            if not reservation:
                raise HTTPException(status_code=404, detail="Reservation not found")
            response = {
                "email": reservation["email"],
                "movie": reservation["movie"],
                "reservation_date": reservation["reservation_date"],
                "reservation_time": reservation["reservation_time"],
                "tickets": reservation["tickets"],
                "seats": reservation["seats"],
                "transaction_id": reservation["transaction_id"],
                "order_id": reservation["order_id"],
                "price": reservation["price"]
            }
    return response

@app.get("/all-user-reservations")
async def get_all_user_reservations(email: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Reservations WHERE email = %s", (email,))
            reservations = cursor.fetchall()
            if not reservations:
                raise HTTPException(status_code=404, detail="Reservations not found")
            response = []
            for reservation in reservations:
                response.append({
                    "email": reservation["email"],
                    "movie": reservation["movie"],
                    "reservation_date": reservation["reservation_date"],
                    "reservation_time": reservation["reservation_time"],
                    "tickets": reservation["tickets"],
                    "seats": reservation["seats"],
                    "transaction_id": reservation["transaction_id"],
                    "order_id": reservation["order_id"],
                    "price": reservation["price"],
                    "payment_succeeded": reservation["payment_succeeded"]
                })
    return response

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
            cursor.execute("SELECT password_hash,email,created_at,id,username,first_name,last_name,phone_number,is_email_verified FROM Users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user or not sha256_crypt.verify(password, user["password_hash"]):
                raise HTTPException(status_code=404, detail="User not found")
            response= {
                'email': user['email'],
                'created_at': user['created_at'],
                'id': user['id'],
                'username': user['username'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'phone_number': user['phone_number'],
                'is_email_verified': user['is_email_verified']
            }
    return response

@app.put("/profile")
async def update_user(email: str, password: str, username: str, first_name: str,
                      last_name: str, phone_number: str, is_email_verified: bool):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT password_hash FROM Users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user or not sha256_crypt.verify(password, user["password_hash"]):
                raise HTTPException(status_code=404, detail="User not found or incorrect password")

            cursor.execute("""
                UPDATE Users
                SET username = %s,
                    first_name = %s,
                    last_name = %s,
                    phone_number = %s,
                    is_email_verified = %s
                WHERE email = %s
            """, (username, first_name, last_name, phone_number, is_email_verified, email))
            conn.commit()

    return JSONResponse(status_code=200, content={"message": "Profile updated successfully"})

@app.post("/payment-status")
async def update_payment_status(transaction_id: str, order_id: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE Reservations SET payment_succeeded = true WHERE transaction_id = %s AND order_id = %s", (transaction_id, order_id))
        conn.commit()
    return JSONResponse(status_code=201, content={"message": True})

# por cada pagina que avanza el usuario le sumamos 2 punto, en tickets tiene que tener 3 otherwise lo llevamos a index, porque
# aunque no vaya a afectar la base puede interactuar con la aplicacion y no queremos eso. poner un point count en la db y ver si es el correcto para navegar las distintas paginas
# login == puntaje 2 , tickets ==3 otherwise alert(stop right there! and href to index.html

# discount applied column? true/false default false
# price with discount column default null

# css and decorations