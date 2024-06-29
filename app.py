from sanic import Sanic, response
from sanic.exceptions import InvalidUsage
from sanic.request import Request
from sanic.response import json
from sqlalchemy import or_

from models import get_db, Contact

app = Sanic("identity_reconciliation")

def find_contacts(db, email=None, phone_number=None):
    # Querying the database to find any elements that have the same email or phone number
    query = db.query(Contact).filter(
        or_(
            Contact.email == email,
            Contact.phoneNumber == phone_number
        )
    )
    return query.all() # retriveing all the elements that mathc the query


def consolidate_contacts(db, existing_contacts, new_email=None, new_phone_number=None):
    first_contact = min(existing_contacts, key=lambda c: c.createdAt) # element created first

    if first_contact.linkPrecedence == 'primary':
        primary_contact = first_contact
        if len(existing_contacts) == 1: # find all the secondary elements if we already dont have it
            existing_contacts = db.query(Contact).filter(Contact.linkedId == primary_contact.id).all()
    else:# find the primary element for the given query
        primary_contact = db.query(Contact).filter(Contact.id == first_contact.linkedId).first()
    secondary_contacts = [c for c in existing_contacts if c != primary_contact]
    # store email and phone numbers
    emails = list({c.email for c in existing_contacts if c.email})
    phone_numbers = list({c.phoneNumber for c in existing_contacts if c.phoneNumber})
    # store primary element details
    if primary_contact.email not in emails: emails.append(primary_contact.email)
    if primary_contact.phoneNumber not in phone_numbers: phone_numbers.append(primary_contact.phoneNumber)
    # either of the elements are not stored in the db, store it
    if new_email and new_email not in emails:
        new_contact = Contact(email=new_email, phoneNumber=new_phone_number, linkedId=primary_contact.id, linkPrecedence='secondary')
        db.add(new_contact)
        contact = db.query(Contact).filter(Contact.email == new_email).filter(Contact.phoneNumber == new_phone_number).filter(Contact.linkedId == primary_contact.id).first()
        secondary_contacts.append(contact)
        emails.append(new_email)
    if new_phone_number and new_phone_number not in phone_numbers:
        new_contact = Contact(email=new_email, phoneNumber=new_phone_number, linkedId=primary_contact.id, linkPrecedence='secondary')
        db.add(new_contact)
        contact = db.query(Contact).filter(
            Contact.phoneNumber == new_phone_number).filter(Contact.email == new_email).filter(Contact.linkedId == primary_contact.id).first()
        secondary_contacts.append(contact)
        secondary_contacts.append(new_contact)
        phone_numbers.append(new_phone_number)

    secondary_contact_ids = [c.id for c in secondary_contacts]

    # Update existing secondary contacts to point to the primary contact
    for contact in secondary_contacts:
        contact.linkedId = primary_contact.id
        contact.linkPrecedence = 'secondary'
        db.commit()

    return {
        "primaryContactId": primary_contact.id,
        "emails": emails,
        "phoneNumbers": phone_numbers,
        "secondaryContactIds": secondary_contact_ids
    }


def create_or_update_contact(db, email=None, phone_number=None):
    existing_contacts = find_contacts(db, email, phone_number) # querying the data from db
    if existing_contacts: # generating output if the user already exists
        return consolidate_contacts(db, existing_contacts, email, phone_number)
    else:
        # Creating a new user identity
        new_contact = Contact(email=email, phoneNumber=phone_number)
        db.add(new_contact)
        db.commit()
        return consolidate_contacts(db, [new_contact])


@app.post('/identify')
async def identify(request: Request):
    try:
        # parsing the request
        data = request.json
        email = data.get('email')
        phone_number = data.get('phoneNumber')

        db = get_db()# getting the database connection
        contact_info = create_or_update_contact(db, email, phone_number)
        db.close()# closing database connection

        return json({"contact": contact_info})
    except InvalidUsage as e:
        return json({"error": str(e)}, status=400)
    except Exception as e:
        # Log the error and return a generic error message
        print(f"Error creating user: {str(e)}")
        return json({"error": "Internal server error"}, status=500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
