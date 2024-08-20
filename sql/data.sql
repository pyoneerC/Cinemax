INSERT INTO Users (
    username, email, password_hash, first_name, last_name, profile_picture,
    phone_number, is_email_verified, is_active, last_login, ip_address,
    latitude, longitude, country, city
)
VALUES
    ('johndoe', 'johndoe@example.com', 'hashed_password_123', 'John', 'Doe',
    'https://example.com/profiles/johndoe.jpg', '+1234567890', TRUE, TRUE,
    '2024-08-19 10:00:00', '192.168.1.1', 40.7128, -74.0060, 'United States', 'New York'),

    ('janedoe', 'janedoe@example.com', 'hashed_password_456', 'Jane', 'Doe',
    'https://example.com/profiles/janedoe.jpg', '+0987654321', FALSE, TRUE,
    '2024-08-18 08:30:00', '172.16.254.1', 34.0522, -118.2437, 'United States', 'Los Angeles'),

    ('mikesmith', 'mikesmith@example.com', 'hashed_password_789', 'Mike', 'Smith',
    NULL, NULL, TRUE, TRUE,
    '2024-08-17 15:45:00', '203.0.113.195', 51.5074, -0.1278, 'United Kingdom', 'London'),

    ('emilybrown', 'emilybrown@example.com', 'hashed_password_101', 'Emily', 'Brown',
    'https://example.com/profiles/emilybrown.jpg', '+1122334455', TRUE, FALSE,
    '2024-08-16 12:15:00', '8.8.8.8', 48.8566, 2.3522, 'France', 'Paris'),

    ('chrisjohnson', 'chrisjohnson@example.com', 'hashed_password_202', 'Chris', 'Johnson',
    NULL, '+1231231234', FALSE, TRUE,
    '2024-08-15 09:00:00', '8.8.4.4', -33.8688, 151.2093, 'Australia', 'Sydney');
