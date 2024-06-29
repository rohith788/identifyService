from datetime import datetime

import sanic
import json
from sanic.exceptions import InvalidUsage
from models import get_db, Users

app = sanic.Sanic("user_service")
def create_contact(email, phoneNumber, primary_contact_id=None, secondary_contact_ids=None):
    contact = {
        "emails": list(email) if email else [],
        "phoneNumbers": list(phoneNumber) if phoneNumber else [],
    }
    if primary_contact_id:
        contact["primaryContatctId"] = primary_contact_id
    if secondary_contact_ids:
        contact["secondaryContactIds"] = list(secondary_contact_ids)
    return contact
async def addUser(email, phoneNumber, linkedID, flag):
    db = get_db()
    newUser = Users(email=email, phoneNumber=phoneNumber, created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
                    linkedID=linkedID, linkedPrecidnece=flag)
    db.add(newUser)
    db.commit()
    db.close()

@app.post("/v1/identify")
async def create_user(request):
    #update secondary contact logic
        # chekc if same emial and phone number exists
    try:
        data = request.json
        email = data.get("email")
        phoneNumber = data.get("phoneNumber")  # Adjust field name
        db = get_db()
        flag = "Primary"
        linkedID = None
        emails = set()
        secondaryIds = set()
        phoneNumbers = set()

        q1 = db.query(Users).filter((Users.email == email)).first()
        q2 = db.query(Users).filter((Users.phoneNumber == phoneNumber)).first()
        if q1 and q1 == q2 and q1.linkedPrecidnece == 'Primary':
            linkedID = q1.id
            if q1.email != None: emails.add(q1.email)
            if q1.phoneNumber != None: phoneNumbers.add(q1.phoneNumber)
        elif q1.linkedPrecidnece == 'Primary' and q2.linkedPrecidnece == 'Primary':
            if q1.id < q2.id:
                linkedID = q1.id
                q2.linkedPrecidnece = 'Secondary'
                q2.linkedID = linkedID
                if q1.email != None: emails.add(q1.email)
                if q1.phoneNumber != None: phoneNumbers.add(q1.phoneNumber)
            else:
                linkedID = q2.id
                q1.linkedPrecidnece = 'Secondary'
                q1.linkedID = linkedID
                if q2.email != None: emails.add(q2.email)
                if q2.phoneNumber != None: phoneNumbers.add(q2.phoneNumber)

        existingUser = db.query(Users).filter(Users.linkedID == linkedID).all()

        if len(existingUser) > 0:
            flag = "Secondary"
            for user in existingUser:
                if user.linkedPrecidnece == "Primary":
                    temp = db.query(Users).filter((Users.email == user.email) & (Users.phoneNumber == user.phoneNumber)).first()
                    temp.linkedPrecidnece = "Secondary"
                    temp.linkedID = linkedID
                    secondaryIds.add(user.id)
                else:
                    secondaryIds.add(user.id)
                if user.email != None: emails.add(user.email)
                if user.phoneNumber != None: phoneNumbers.add(user.phoneNumber)
        q1 = db.query(Users).filter((Users.email == email)).first()
        q2 = db.query(Users).filter((Users.phoneNumber == phoneNumber)).first()
        addUsr = None
        if (not q1 and email is not None) or (not q2 and phoneNumber is not None):
            addUsr = addUser(email=email, phoneNumber=phoneNumber,linkedID=linkedID, flag=flag)
        if addUsr: await addUsr
        # db.commit()
        db.close()
        # Assuming primary_contact_id and secondary_contact_ids are generated elsewhere
        contact = create_contact(emails, phoneNumbers, primary_contact_id=linkedID, secondary_contact_ids=secondaryIds)
        return sanic.response.json({"contact": contact})
    except InvalidUsage as e:
        return sanic.response.json({"error": str(e)}, status=400)
    except Exception as e:
        # Log the error and return a generic error message
        print(f"Error creating user: {str(e)}")
        return sanic.response.json({"error": "Internal server error"}, status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
