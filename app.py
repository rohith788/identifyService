from datetime import datetime

import sanic
import json
from sanic.exceptions import InvalidUsage
from models import get_db, Users

app = sanic.Sanic("user_service")
def create_contact(email, phone_number, primary_contact_id=None, secondary_contact_ids=None):
    contact = {
        "emails": [email] if email else [],
        "phoneNumbers": [phone_number] if phone_number else [],
    }
    if primary_contact_id:
        contact["primaryContatctId"] = primary_contact_id
    if secondary_contact_ids:
        contact["secondaryContactIds"] = secondary_contact_ids
    return contact

@app.post("/orders")
async def create_user(request):
    try:
        data = request.json
        email = data.get("email")
        phone_number = data.get("phoneNumber")  # Adjust field name
        user_details = data.get("order_details")

        # Validate data
        if not user_details:
            raise InvalidUsage("Missing order details")

        # Check for existing order with same contact info
        # (modify logic if needed based on your specific contact identification)
        db = get_db()
        existing_order = db.query(Users).filter((Users.email == email) | (Users.phone_number == phone_number)).first()
        db.close()

        if existing_order:
            return sanic.response.json({"message": "Duplicate order detected"}, status=409)

        # Create new order
        new_order = Users(email=email, phone_number=phone_number, created_at=datetime.utcnow(), order_details=user_details)
        db = get_db()
        db.add(new_order)
        db.commit()
        db.close()

        # Assuming primary_contact_id and secondary_contact_ids are generated elsewhere
        contact = create_contact(email, phone_number, primary_contact_id=1, secondary_contact_ids=[23])

        return sanic.response.json({"contact": contact})

    except InvalidUsage as e:
        return sanic.response.json({"error": str(e)}, status=400)
    except Exception as e:
        # Log the error and return a generic error message
        app.logger.error(f"Error creating order: {str(e)}")
        return sanic.response.json({"error": "Internal server error"}, status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
