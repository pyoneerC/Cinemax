INSERT INTO Users (id, email, password_hash) VALUES
  ('123e4567-e89b-12d3-a456-426614174000', 'user1@example.com', 'hashed_password_1'),
  ('123e4567-e89b-12d3-a456-426614174001', 'user2@example.com', 'hashed_password_2');

INSERT INTO Reservations (user_id, email, movie, reservation_date, reservation_time, seats, tickets, order_id, transaction_id)
VALUES
  (
    '123e4567-e89b-12d3-a456-426614174000',
    'user1@example.com',
    'The Matrix',
    '2024-09-01',
    '19:30',
    '["A1", "A2", "B1"]',
    3,
    'ORD123456789',
    'TRANS1234567890'
  );
