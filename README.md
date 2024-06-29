# Contact Identity Reconciliation Service

This service consolidates contact information to reconcile identities based on email and phone number.

## Features

- Identifies and consolidates contact entries based on provided email and phone number.
- Ensures no duplicate primary contacts are created.
- Links secondary contact information to a primary contact.

## Tech Stack

- **Python**: The primary language for the service.
- **Sanic**: A Python 3.7+ web server and web framework that's written to go fast.
- **SQLite**: A C library that provides a lightweight disk-based database.
- **SQLAlchemy**: The Python SQL toolkit and Object Relational Mapper.

## Hosted Service

The service is hosted on Render.com and can be accessed at:

[https://identifyservice.onrender.com/identify](https://identifyservice.onrender.com/identify)

## API Usage

### Identify Endpoint

**URL**: `/identify`

**Method**: `POST`

**Request Body**:

- `email`: (Optional) The email of the contact.
- `phoneNumber`: (Optional) The phone number of the contact.

**Example Request**:

```json
{
  "email": "example@domain.com",
  "phoneNumber": "1234567890"
}
```
**Response Body**:

- `primaryContactId`: The ID of the primary contact.
- `emails`: List of emails associated with the contact.
- `phoneNumbers`: List of phone numbers associated with the contact.
- `secondaryContactIds`: List of IDs of secondary contacts linked to the primary contact.

**Example Response**:
```json
{
  "contact": {
    "primaryContactId": 1,
    "emails": [
      "example@domain.com"
    ],
    "phoneNumbers": [
      "1234567890"
    ],
    "secondaryContactIds": [
      2, 3
    ]
  }
}

```

## Local Setup
1) Clone the repository:
```commandline
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```
2) Install dependencies:
```commandline
pip install -r requirements.txt
```
3) Run the service:
```commandline
python app.py
```