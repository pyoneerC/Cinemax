CREATE TABLE IF NOT EXISTS Reservations (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    email VARCHAR(255) NOT NULL,
    movie VARCHAR(255) NOT NULL,
    reservation_date DATE DEFAULT CURRENT_DATE,
    reservation_time TIME NOT NULL,
    seats TEXT DEFAULT '[]',
    tickets INT DEFAULT 0,
    order_id VARCHAR(255) UNIQUE,
    transaction_id VARCHAR(255) UNIQUE,
    payment_succeeded BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    CONSTRAINT fk_email FOREIGN KEY (email) REFERENCES Users(email) ON DELETE CASCADE,
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'),
    CONSTRAINT chk_time CHECK (reservation_time >= '00:00:00' AND reservation_time <= '23:59:59')
);