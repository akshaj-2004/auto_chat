import json
from sqlalchemy.orm import Session
from app.schemas.registration import RegistrationCreate, RegistrationUpdate
from app.services.reg_service import (
    create_registration,
    get_registration,
    get_registration_by_email,
    update_registration,
    delete_registration,
)

class RegistrationTools:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload_str: str) -> str:
        print(f"[DEBUG] create() called with payload: {payload_str}, type: {type(payload_str)}")
        try:
            if isinstance(payload_str, dict):
                payload = payload_str
            else:
                payload = json.loads(payload_str)
            print(f"[DEBUG] Parsed payload: {json.dumps(payload, indent=2)}")

            for field in ['full_name', 'email', 'phone', 'date_of_birth', 'address']:
                value = payload.get(field, 'MISSING')
                print(f"[DEBUG]   {field}: '{value}' (type: {type(value).__name__})")

            forbidden_values = {
                'full_name': ['john doe', 'jane doe', 'test user', 'example user', 'user name'],
                'email': ['john.doe@example.com', 'jane.doe@example.com', 'test@example.com',
                         'user@example.com', 'example@example.com'],
                'phone': ['1234567890', '0000000000', '9999999999'],
            }

            for field, forbidden_list in forbidden_values.items():
                value = str(payload.get(field, '')).lower().strip()
                if value in forbidden_list:
                    error_msg = (
                        f"TELL THE USER: I cannot use example or placeholder data like '{payload.get(field)}'. "
                        f"Please provide the REAL {field.replace('_', ' ')} for the person you want to register."
                    )
                    print(f"[ERROR] Rejected default value for {field}: {value}")
                    return json.dumps({"error": error_msg, "rejected_field": field})

            required_fields = ['full_name', 'email', 'phone', 'date_of_birth']
            missing_fields = [f for f in required_fields if not payload.get(f) or payload.get(f) == '']

            if missing_fields:
                error_msg = (
                    "TOOL ERROR: Missing all required information. "
                    "TELL THE USER: 'I'd be happy to help you register a new user! "
                    "Please provide the following information: "
                    "full name, email address, phone number, date of birth (YYYY-MM-DD format), and address (optional).'"
                )
                print(f"[ERROR] {error_msg}")
                return json.dumps({"error": error_msg, "missing_fields": missing_fields})

            data = RegistrationCreate(**payload)
            print(f"[DEBUG] Created RegistrationCreate object: {data}")
        except ValueError as e:
            error_msg = str(e)
            print(f"[ERROR] Validation error: {error_msg}")
            if "date_of_birth" in error_msg:
                friendly_msg = "Invalid date of birth. Please provide a date in YYYY-MM-DD format (e.g., 1990-01-01)."
            elif "email" in error_msg.lower():
                friendly_msg = "Invalid email address. Please provide a valid email (e.g., user@example.com)."
            elif "phone" in error_msg.lower():
                friendly_msg = "Invalid phone number. Please provide a valid phone number (10-15 digits)."
            else:
                friendly_msg = f"Validation error: {error_msg}"
            return json.dumps({"error": friendly_msg})
        except Exception as e:
            error_msg = f"Error parsing input: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Full payload was: {payload_str}")
            return json.dumps({"error": "Invalid input format. Please provide all required fields correctly."})

        try:
            obj = create_registration(self.db, data)
            print(f"[DEBUG] Created registration with ID: {obj.id}")
            return json.dumps({
                "id": str(obj.id),
                "status": "success",
                "message": f"Successfully created registration for {obj.full_name}"
            })
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] {error_msg}")

            if "duplicate key" in error_msg.lower() or "unique constraint" in error_msg.lower():
                if "email" in error_msg.lower():
                    return json.dumps({"error": f"A user with email {data.email} already exists. Please use a different email address."})
                else:
                    return json.dumps({"error": "This user already exists in the system."})

            return json.dumps({"error": "Failed to create registration. Please try again."})

    def _resolve_registration(self, identifier: str):
        import uuid
        reg = None
        try:
            uuid_obj = uuid.UUID(identifier)
            reg = get_registration(self.db, uuid_obj)
        except (ValueError, AttributeError):
            pass

        if not reg:
            reg = get_registration_by_email(self.db, identifier)
        return reg

    def get(self, identifier: str) -> str:
        reg = self._resolve_registration(identifier)

        if not reg:
            return json.dumps({"error": f"User not found with identifier: {identifier}. Please check the email or ID."})

        return json.dumps({
            "id": str(reg.id),
            "full_name": reg.full_name,
            "email": reg.email,
            "phone": reg.phone,
            "date_of_birth": str(reg.date_of_birth),
            "address": reg.address
        })

    def update(self, payload_str: str) -> str:
        try:
            if isinstance(payload_str, dict):
                payload = payload_str
            else:
                payload = json.loads(payload_str)
            reg_id = payload.get("id")
            updates = RegistrationUpdate(**payload.get("updates", {}))
        except Exception as e:
            return json.dumps({"error": str(e)})

        reg = self._resolve_registration(reg_id)
        if not reg:
            return json.dumps({"error": f"User not found with identifier: {reg_id}. Please check the email or ID."})

        updated = update_registration(self.db, reg, updates)
        return json.dumps({"status": "ok", "id": str(updated.id)})

    def delete(self, identifier: str) -> str:
        reg = self._resolve_registration(identifier)

        if not reg:
            return json.dumps({"error": f"User not found with identifier: {identifier}. Please check the email or ID."})

        delete_registration(self.db, reg)
        return json.dumps({"status": "deleted"})
