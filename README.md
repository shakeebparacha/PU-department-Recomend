# PU Merit Recommendation System - Django Version

A comprehensive web application for Punjab University students to discover suitable academic programs based on their merit percentage.

## Features

✨ **Core Features:**
- 🧮 Merit Calculator - Get personalized program recommendations
- 🏢 Faculty Browsing - Filter programs by faculty
- 📍 Campus Selection - Find programs at your preferred campus
- 📅 Semester & Year Filters - Browse by specific intake periods
- 📱 Mobile-Friendly Design - Fully responsive interface
- 🎨 Modern UI with Bootstrap 5 - Professional styling

## 📋 Requirements

- Python 3.8+
- Django 4.2+
- Pandas for data processing
- SQLite3 (included with Python)

## 🚀 Quick Start

### 1. Clone or Extract the Project
```bash
cd pu-merit-app
```

### 2. Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser (Optional - for Admin Panel)
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## 📂 Project Structure

```
pu-merit-app/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── data/
│   └── merit_data.csv       # Merit cutoff data
├── pu_merit/                # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── merit/                   # Django app
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── urls.py             # URL routing
│   └── admin.py            # Admin configuration
├── templates/              # HTML templates
│   ├── base.html           # Base template with header/footer
│   └── merit/
│       ├── home.html
│       ├── calculator.html
│       └── recommendations.html
└── static/                 # Static files (CSS, JS, images)
```

## 📖 Pages

### 1. Home Page
- Welcome section with features overview
- "How it Works" guide
- Call-to-action buttons
- Professional header and footer

### 2. Merit Calculator
- Input merit percentage
- Filter by:
  - Faculty
  - Campus
  - Semester
  - Year
- View results with difficulty categorization:
  - ✅ **Safe** - Program cutoff 10%+ below your merit
  - ⚠️ **Moderate** - Program cutoff within 10% of your merit
  - ⚠️⚠️ **Risky** - Program cutoff above your merit but within 10%
  - ❌ **Not Eligible** - Program cutoff more than 10% above your merit

### 3. Department Recommendations
- Browse programs by faculty
- Browse programs by campus
- Upcoming features overview

## 🎨 Design Features

- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **Bootstrap 5** - Modern, accessible components
- **Gradient Colors** - Professional purple gradient theme
- **Font Awesome Icons** - Beautiful icons throughout
- **Smooth Animations** - Cards and buttons with hover effects
- **Professional Header** - Sticky navigation with active page indicator
- **Footer** - Complete footer with links and social media

## 🔧 Customization

### Adding New Programs
Place your merit data in `data/merit_data.csv` with columns:
```
Faculty, Program, Merit_Percentage, Campus, Semester, Year
```

### Modifying Colors
Edit the color variables in `templates/base.html`:
```css
/* Primary Gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Changing Logo/Title
Update the navbar brand in `templates/base.html`:
```html
<a class="navbar-brand" href="...">
    <i class="fas fa-graduation-cap"></i>
    Your App Name
</a>
```

## 📝 Database Models

### MeritData Model
```python
- faculty (CharField)
- program (CharField)
- merit_percentage (FloatField)
- campus (CharField)
- semester (CharField)
- year (IntegerField)
```

## 🔒 Security Notes

⚠️ **For Production:**
1. Set `DEBUG = False` in settings.py
2. Change `SECRET_KEY` to a secure random value
3. Set `ALLOWED_HOSTS` to your domain
4. Use environment variables for sensitive data
5. Configure proper database (PostgreSQL recommended)
6. Set up proper static and media file serving

## 🐛 Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001  # Use different port
```

### Static Files Not Loading
```bash
python manage.py collectstatic
```

### Database Errors
```bash
python manage.py flush     # Reset database
python manage.py migrate   # Re-apply migrations
```

## 📦 Deployment

For production deployment:
1. Use a production server (Gunicorn, uWSGI)
2. Set up nginx reverse proxy
3. Use PostgreSQL or MySQL
4. Configure SSL/HTTPS
5. Set up proper error logging

## 🤝 Contributing

To enhance the application:
1. Improve the Merit Calculator algorithm
2. Add user authentication
3. Implement program details pages
4. Add comparison feature
5. Create PDF export functionality

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review Django documentation
- Verify your data format in merit_data.csv

## 📄 License

This project is created for Punjab University students.

## 🎓 Version History

- **v1.0** - Initial Django version with home, calculator, and recommendations pages
- **v0.1** - Original Streamlit version

---

**Last Updated:** 2024
**Django Version:** 4.2+
**Python Version:** 3.8+
