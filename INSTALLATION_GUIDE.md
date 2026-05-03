# 🚀 PU Merit System - Installation & Setup Guide

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Running the Application](#running-the-application)
4. [File Structure](#file-structure)
5. [Troubleshooting](#troubleshooting)
6. [Production Deployment](#production-deployment)

---

## 💻 System Requirements

- **Python**: 3.8 or higher
- **pip**: Package manager (comes with Python)
- **Git** (optional, for version control)
- **Modern Browser**: Chrome, Firefox, Safari, or Edge

### Check Your Python Version

**Windows:**
```bash
python --version
```

**macOS/Linux:**
```bash
python3 --version
```

If you don't have Python, download it from [python.org](https://www.python.org/downloads/)

---

## 📦 Installation Steps

### Step 1: Navigate to Project Directory

**Windows:**
```bash
cd "path\to\pu-merit-app"
```

**macOS/Linux:**
```bash
cd /path/to/pu-merit-app
```

### Step 2: Create Virtual Environment

A virtual environment keeps your project dependencies isolated.

**Windows:**
```bash
python -m venv venv
```

**macOS/Linux:**
```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal line when activated.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Django 4.2.11
- Pandas 2.1.4
- Other required packages

### Step 5: Set Up Database

```bash
python manage.py migrate
```

This creates the SQLite database file (`db.sqlite3`).

### Step 6: (Optional) Create Admin User

To access the admin dashboard:

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Username: (choose a username)
- Email: (your email)
- Password: (choose a strong password)
- Confirm Password: (repeat password)

---

## ▶️ Running the Application

### Start Development Server

```bash
python manage.py runserver
```

**Output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Open in Browser

Visit: **http://localhost:8000/**

### Stop Server

Press `Ctrl+C` in the terminal

---

## 📂 File Structure

```
pu-merit-app/
│
├── manage.py                    # Django command manager
├── requirements.txt             # Python dependencies
├── setup.py                     # Automated setup script
├── README.md                    # Project documentation
├── .gitignore                   # Git ignore file
├── .env.example                 # Environment variables template
│
├── data/
│   └── merit_data.csv          # Merit data (CSV format)
│
├── pu_merit/                   # Project settings
│   ├── __init__.py
│   ├── settings.py             # Main configuration
│   ├── urls.py                 # URL routing
│   └── wsgi.py                 # WSGI configuration
│
├── merit/                      # Main Django app
│   ├── __init__.py
│   ├── models.py               # Database models
│   ├── views.py                # Business logic
│   ├── urls.py                 # App URLs
│   ├── admin.py                # Admin interface
│   ├── apps.py                 # App configuration
│   └── tests.py                # Unit tests
│
├── templates/
│   ├── base.html               # Base template (header/footer)
│   └── merit/
│       ├── home.html           # Home page
│       ├── calculator.html     # Merit calculator
│       └── recommendations.html # Recommendations page
│
├── static/
│   └── css/
│       └── style.css           # Custom styles
│
└── db.sqlite3                  # Database (auto-created)
```

---

## 🐛 Troubleshooting

### Issue: "Python command not found"

**Solution:**
- Add Python to your system PATH
- Use `python3` instead of `python` on macOS/Linux

### Issue: Port 8000 already in use

**Solution:**
```bash
python manage.py runserver 8001  # Use port 8001
```

### Issue: Static files not loading

**Solution:**
```bash
python manage.py collectstatic --noinput
```

### Issue: Database errors

**Solution:**
```bash
# Reset database (warning: deletes all data)
python manage.py flush

# Reapply migrations
python manage.py migrate
```

### Issue: Import errors

**Solution:**
```bash
# Ensure virtual environment is activated
pip install -r requirements.txt  # Reinstall dependencies
```

### Issue: "No module named 'merit'"

**Solution:**
```bash
# Ensure you're in the correct directory
cd pu-merit-app
python manage.py runserver
```

---

## 🗂️ Data Format

Place your merit data in `data/merit_data.csv` with this structure:

```csv
Faculty,Program,Merit_Percentage,Campus,Semester,Year
Engineering,Software Engineering,82.5,Lahore,Spring,2024
Engineering,Civil Engineering,78.0,Lahore,Spring,2024
Science,Physics,85.0,Islamabad,Fall,2024
Business,Management,80.5,Lahore,Spring,2024
```

**Column Details:**
- **Faculty**: Department name (e.g., Engineering, Science)
- **Program**: Degree name (e.g., B.S. Software Engineering)
- **Merit_Percentage**: Minimum merit percentage required
- **Campus**: University campus location
- **Semester**: Spring, Fall, or Summer
- **Year**: Admission year

---

## 🔧 Common Customizations

### Change App Title

Edit `templates/base.html`:
```html
<title>Your New Title - PU Merit System</title>
```

### Change Color Scheme

Edit `templates/base.html` CSS section:
```css
--primary-color: #667eea;      /* Change primary color */
--secondary-color: #764ba2;    /* Change secondary color */
```

### Add Your Logo

Replace the icon in `templates/base.html`:
```html
<i class="fas fa-graduation-cap"></i>  <!-- Change this -->
```

### Modify Navigation Links

Edit navigation in `templates/base.html`:
```html
<ul class="navbar-nav ms-auto">
    <!-- Add or remove nav items here -->
</ul>
```

---

## 📦 Admin Dashboard

Access the Django admin panel:

1. **Create admin user** (if not done):
   ```bash
   python manage.py createsuperuser
   ```

2. **Visit admin panel**: http://localhost:8000/admin

3. **Login** with your superuser credentials

4. **Manage** programs, faculties, and other data

---

## 🚀 Production Deployment

Before deploying to production, make these changes:

### 1. Update Settings

Edit `pu_merit/settings.py`:
```python
DEBUG = False  # Set to False
SECRET_KEY = 'generate-a-new-secure-key'  # Use a secure key
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

### 2. Collect Static Files

```bash
python manage.py collectstatic
```

### 3. Use Production Server

Install Gunicorn:
```bash
pip install gunicorn
```

Run with Gunicorn:
```bash
gunicorn pu_merit.wsgi:application
```

### 4. Database

Switch to PostgreSQL for better performance:
```bash
pip install psycopg2-binary
```

Update `DATABASES` in settings.py.

### 5. HTTPS

Use SSL certificates (Let's Encrypt is free)

### 6. Environment Variables

Create `.env` file with sensitive data:
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
```

---

## 📞 Support & Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Python Documentation**: https://docs.python.org/3/
- **Bootstrap 5 Docs**: https://getbootstrap.com/docs/5.0/
- **Font Awesome Icons**: https://fontawesome.com/

---

## ✅ Quick Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database migrated (`python manage.py migrate`)
- [ ] Data file present in `data/merit_data.csv`
- [ ] Server running (`python manage.py runserver`)
- [ ] Application opens at http://localhost:8000/

---

**You're all set! 🎉 Enjoy your PU Merit System!**

For additional help, refer to the README.md file or check the Django documentation.
