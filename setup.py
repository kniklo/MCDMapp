from app import db, app

def setup_database():
    with app.app_context():
        db.create_all()
        print("✅ Database created successfully.")

if __name__ == '__main__':
    setup_database()
