import sys
import os

# Add backend to path so we can import app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.infrastructure.models.iam import Role
from uuid import uuid4

def seed_roles():
    print("Seeding default roles...")
    db = SessionLocal()
    
    default_roles = [
        "Administrator",
        "SOC Analyst",
        "Threat Hunter",
        "Incident Responder",
        "Read Only"
    ]
    
    for role_name in default_roles:
        existing_role = db.query(Role).filter(Role.name == role_name).first()
        if not existing_role:
            new_role = Role(id=uuid4(), name=role_name)
            db.add(new_role)
            print(f"Added role: {role_name}")
        else:
            print(f"Role already exists: {role_name}")
            
    db.commit()
    db.close()
    print("Roles seeded successfully.")

if __name__ == "__main__":
    seed_roles()
