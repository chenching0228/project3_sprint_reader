from app.database import engine, Base
from app import models

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully.")

if __name__ == "__main__":
    create_tables()