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

## 📦 Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Set Up a Virtual Environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: source venv/Scripts/activate
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create your own `.env` file by copying the example:

```bash
cp .env.example .env
```

Edit `.env` and set your local MySQL credentials:

```env
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_NAME=mcdmapp
SECRET_KEY=yoursecretkey
```

Or provide full URI using `DATABASE_URL`.

---

## 🧱 MySQL Setup

Make sure your MySQL server is running locally (`localhost:3306`).  
You **must create the database schema manually once** (only this step is manual):

1. Open your MySQL console:

```bash
mysql -u root -p
```

2. Run this command inside MySQL shell:

```sql
CREATE DATABASE mcdmapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. Exit MySQL shell:

```sql
exit
```

> 💡 *Tip:* This is a one-time setup. After this, all tables will be created automatically.

---

## 🗃️ Initialize Database Tables

Run this once to create all required tables according to your models:

```bash
python setup.py
```

> This script connects to your MySQL database and creates all tables automatically.

---

## ▶️ Run the Application

```bash
python dmapp.py
```

The app will start on [http://localhost:5000](http://localhost:8000)

---

## 🖼️ Demo Video

> A video showing how to create tasks, enter expert evaluations, and see results will be added here.

---

## 📁 Project Structure

```
YOUR_REPO_NAME/
├── app/              # Application logic
├── templates/        # Jinja2 HTML templates
├── static/           # CSS, JS, etc.
├── migrations/       # Alembic migrations (optional)
├── dmapp.py          # App entrypoint
├── setup.py          # Database initialization script
├── config.py         # Configuration (uses .env)
├── .env.example      # Example environment config
├── requirements.txt
└── README.md
```

---

## ❓ Common Issues

- ❗ MySQL not running:  
  `pymysql.err.OperationalError: (2003, "Can't connect to MySQL server...")`  
  → Start MySQL and check `.env` settings.

- ❗ Missing `.env`:  
  → Make sure `.env` exists and contains correct settings.

- ❗ Permission errors on migration:  
  → Ensure your MySQL user has privileges for schema changes.

---

## 📜 License

This project is open-source under the MIT License.

---

## ✨ Contributions Welcome

Fork this repo and submit pull requests to improve it!
