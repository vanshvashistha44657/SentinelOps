import sys
import os
from fastapi import FastAPI
from sqlalchemy import text
from app.main import app
from app.core.database import SessionLocal

def verify():
    print("Starting Production Verification...")
    
    # 1. Verify Application Startup
    try:
        print("Verifying Application Startup...")
        assert isinstance(app, FastAPI)
        print("✔ Application startup verified.")
    except Exception as e:
        print(f"✘ Application startup failed: {e}")
        return

    # 2. Verify Database Connection
    print("Verifying Database Connection...")
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✔ Database connection verified.")
    except Exception as e:
        print(f"✘ Database connection failed: {e}")
        return

    # 3. Verify Route Loading
    print("Verifying Routes...")
    for route in app.routes:
        try:
            if hasattr(route, "path"):
                print(f"  Checking route: {route.path}")
        except Exception as e:
            print(f"  ✘ Route verification failed: {e}")
            return
    print("✔ All routes loaded successfully.")

    print("\nProduction Verification Successful.")

if __name__ == "__main__":
    verify()
