import sys
import os

# Add backend to path so we can import app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.infrastructure.models.iam import Role, Permission
from uuid import uuid4

def seed_data():
    print("Seeding roles and permissions...")
    db = SessionLocal()
    
    # Define all required permissions
    permission_list = [
        "dashboard:view",
        "alerts:view", "alerts:create", "alerts:edit", "alerts:delete",
        "incidents:view", "incidents:create", "incidents:edit",
        "cases:view", "cases:create", "cases:edit", "cases:close",
        "hunting:search", "hunting:save",
        "admin:write", "admin:read"
    ]
    
    # Create Permissions
    permission_map = {}
    for p_name in permission_list:
        p = db.query(Permission).filter(Permission.name == p_name).first()
        if not p:
            p = Permission(id=uuid4(), name=p_name)
            db.add(p)
        permission_map[p_name] = p
        
    # Create Roles and map permissions
    roles_config = {
        "Administrator": permission_list,
        "SOC Analyst": ["dashboard:view", "alerts:view", "incidents:view", "cases:view", "hunting:search"],
    }
    
    for role_name, permissions in roles_config.items():
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(id=uuid4(), name=role_name)
            db.add(role)
        
        # Sync permissions
        role.permissions = [permission_map[p] for p in permissions]
            
    db.commit()
    db.close()
    print("Roles and permissions seeded successfully.")

if __name__ == "__main__":
    seed_data()
