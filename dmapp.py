from app import app, db
from config import Config

app.config.from_object(Config)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False, port=8000, host="0.0.0.0")
