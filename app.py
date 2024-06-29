from datetime import datetime

import sanic
import json
from sanic.exceptions import InvalidUsage
from models import get_db, Users

app = sanic.Sanic("user_service")
def create_contact(email, phoneNumber, primary_contact_id=None, secondary_contact_ids=None):
    contact = {
        "emails": email if email else [],
        "phoneNumbers": phoneNumber if phoneNumber else [],
    }
    if primary_contact_id:
        contact["primaryContatctId"] = primary_contact_id
    if secondary_contact_ids:
        contact["secondaryContactIds"] = secondary_contact_ids
    return contact

@app.post("/v1/identify")
async def create_user(request):
    #update secondary contact logic
        # chekc if same emial and phone number exists
    try:
        data = request.json
        email = data.get("email")
        phoneNumber = data.get("phoneNumber")  # Adjust field name
        db = get_db()
        existingUser = db.query(Users).filter((Users.email == email) | (Users.phoneNumber == phoneNumber)).all()
        flag = "Primary"
        linkedID = None
        emails = []
        secondaryIds = []
        phoneNumbers = []
        if len(existingUser)>0:
            flag = "Secondary"
            for user in existingUser:
                if user.linkedPrecidnece == "Primary":
                    if linkedID is None:
                        linkedID = user.id
                    else:
                        temp = db.query(Users).filter((Users.email == user.email) & (Users.phoneNumber == user.phoneNumber)).first()
                        temp.linkedPrecidnece = "Secondary"
                        temp.linkedID = linkedID
                        secondaryIds.append(user.id)
                else:
                    secondaryIds.append(user.id)
                emails.append(user.email)
                phoneNumbers.append(user.phoneNumber)
        q1 = db.query(Users).filter((Users.email == email))
        q2 = db.query(Users).filter((Users.phoneNumber == phoneNumber))
        checkUser = q1.intersect(q2).all()
        if len(checkUser) == 0:
            newUser = Users(email=email, phoneNumber=phoneNumber, created_at=datetime.utcnow(), updated_at=datetime.utcnow(), linkedID=linkedID, linkedPrecidnece=flag)
            db.add(newUser)
            db.commit()
        db.close()
        # Assuming primary_contact_id and secondary_contact_ids are generated elsewhere
        contact = create_contact(emails, phoneNumbers, primary_contact_id=linkedID, secondary_contact_ids=secondaryIds)

        return sanic.response.json({"contact": contact})
        # Create new order
    except InvalidUsage as e:
        return sanic.response.json({"error": str(e)}, status=400)
    except Exception as e:
        # Log the error and return a generic error message
        print(f"Error creating order: {str(e)}")
        return sanic.response.json({"error": "Internal server error"}, status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
