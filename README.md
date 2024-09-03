# Cinemax - Cinema Reservation System

Cinemax is a FastAPI-based cinema reservation system that allows users to register, log in, make reservations, and manage their profiles. It includes functionalities for ticket management, seat selection, payment status updates, and applying discounts. This project is part of the Cinemaximo platform, which you can explore [here](https://cinemaximo.netlify.app).

## Features
- User Registration and Login: Secure registration and login system using SHA-256 password hashing.
- Reservation Management: Create, update, and fetch reservation details including tickets, seats, and payment status.
- Profile Management: Update and view user profiles.
- Payment Integration: Manage payment status and apply discounts.
- Step Count: Track and update steps for reservations.

## API Endpoints
1. Root
`GET /`
Returns the version of the connected database.
2. User Registration
`POST /register`
Registers a new user with email and password.
3. User Login and Reservation
`POST /login`
Logs in a user and creates a reservation with a unique transaction and order ID.
4. Ticket Management
`POST /tickets`
Updates the number of tickets and price for a reservation.
5. Seat Selection
`POST /seats`
Updates the seats selected for a reservation.
6. Reservation Details
`GET /reservation-details`
Retrieves details of a reservation using transaction and order IDs.
7. User Reservations
`GET /all-user-reservations`
Fetches all reservations for a specific user email.
8. Password Reset
`PUT /reset`
Resets a user’s password.
9. User Profile
`GET /profile`
Fetches user profile information.

PUT /profile
Updates user profile information.

10. Payment Status
POST /payment-status
Updates the payment status of a reservation.
11. Step Count
PUT /step_count
Increases the step count for a reservation.

GET /step_count
Retrieves the current step count for a reservation.

12. Discount Management
PUT /discount
Applies a discount to a reservation.
Installation
To run this project locally, follow these steps:

Clone the Repository:

```bash
git clone https://github.com/yourusername/cinemax.git
```

Navigate to the Project Directory:

```bash
cd cinemax
```

Create a Virtual Environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install Dependencies:

```bash
pip install -r requirements.txt
```

Set Up Environment Variables:

Ensure you have a .env file with the following content:

```env
DATABASE_URL=your_database_url_here
```
Run the Application:

```bash
uvicorn main:app --reload
```

The application will be available at http://localhost:8000.

## Deployment

For deployment, this project uses Docker. Follow these steps to build and run the Docker container:

Build the Docker Image:

```bash
docker compose up --build
```

Run the Docker Container:

```bash
docker compose up
```

### Contributing

Contributions are welcome! Please submit a pull request or open an issue for discussion.

### License

This project is licensed under the MIT License. See the LICENSE file for details.

### Contact
For any questions or inquiries, please contact [maxcomperatore@gmail.com](mailto:maxcomperatore@gmail.com).