# 🧠 MCDM Decision Support System (FAHP-based)

A Flask-based decision support system (DSS) implementing the Fuzzy Analytic Hierarchy Process (FAHP) for evaluating alternatives (e.g., cosmetic products). Users can create decision tasks, define criteria/alternatives, enter expert judgments, and receive automatic analysis results.

---

## 🚀 Features

- ✅ Full FAHP implementation (fuzzification, consistency check, weight calculation)
- ✅ SQLAlchemy + MySQL support
- ✅ Modular Flask architecture
- ✅ User authentication, task management, expert evaluation workflows
- ✅ AJAX support for dynamic interfaces

---

## 📁 Project Structure

```
mcdmApp/
├── app/                         # Core application package
│   ├── services/                # FAHP logic: сustom step, fuzzification, consistency checks, weight calculation, defuzzification
│   ├── static/                  # Static assets: CSS, JavaScript, images, fonts
│   ├── templates/               # Jinja2 HTML templates
│   ├── tests/                   # tests for FAHP computations and Flask routes
│   ├── __init__.py              # Flask app factory: initializes extensions, blueprints, and config
│   ├── forms.py                 # Flask-WTF forms for user input (e.g., login, task creation, evaluations)
│   ├── models.py                # SQLAlchemy ORM models: User, Task, Criterion, Alternative, Evaluation, etc.
│   ├── routes.py                # Main Flask routes
├── dmapp.py                     # App entry point: runs the Flask app with selected config
├── setup.py                     # Script for initializing the database with sample or default data
├── config.py                    # Centralized application configuration (e.g., database URI, secret key)
├── .env.example                 # Example of environment variables needed to run the app
├── requirements.txt             # Python package dependencies (Flask, SQLAlchemy, etc.)
└── README.md                    

```
---

## ✨ Contributions Welcome

Fork this repo and submit pull requests to improve it!
