# 🎓 PU Merit Recommendation System

A Streamlit web application that helps students from University of the Punjab discover which programs they are eligible for based on their merit score. The app provides personalized recommendations with difficulty levels and generates detailed PDF reports.

## Features

✅ **Merit-Based Filtering**: Enter your merit percentage to find eligible programs  
✅ **Smart Difficulty Levels**: Programs categorized as Safe, Moderate, or Risky based on your merit  
✅ **Multi-Level Filtering**: Filter by Faculty, Campus, Semester Type, and Year  
✅ **Interactive Results**: View all eligible programs in a searchable, sortable table  
✅ **PDF Export**: Download a detailed recommendation report  
✅ **Multi-Year Support**: Compare merit requirements across different years  
✅ **Campus Support**: Includes Main campus and satellite campuses (Gujranwala, Jhelum, Pothohar)  

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or Download** the repository:
```bash
cd pu-merit-app
```

2. **Create a virtual environment** (optional but recommended):
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Usage

### Running Locally

1. **Navigate to the project directory**:
```bash
cd pu-merit-app
```

2. **Run the Streamlit app**:
```bash
streamlit run app.py
```

3. **Open in browser**: The app will automatically open at `http://localhost:8501`

### Using the App

1. **Enter Your Merit**: Input your entrance merit percentage (0-100%)
2. **Select Year**: Choose the academic year you're applying for
3. **Filter Options**: 
   - Select specific faculties (or leave empty for all)
   - Choose campuses (Main, Gujranwala, Jhelum, Pothohar)
   - Select semester types (Morning, Evening, Self Support)
4. **View Results**: See all eligible programs with:
   - Program name and faculty
   - Campus and semester type
   - Cutoff merit percentage
   - Your margin above/below cutoff
   - Difficulty level indicator
5. **Download Report**: Click the download button to get a PDF with all recommendations

## Difficulty Levels Explained

- **Safe ✅**: Your merit is **10%+ above** the program cutoff
  - Highly likely to get admission
  - Good safety choice

- **Moderate ⚠️**: Your merit is **within 10%** of the program cutoff
  - Balanced choice
  - Reasonable chance of admission

- **Risky ⚠️⚠️**: Program cutoff is **above your merit** (but within 10%)
  - Competitive program
  - Lower chance of admission but still possible

## Data

### File Structure
```
pu-merit-app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── data/
    └── merit_data.csv    # Merit cutoff data (2024)
```

### Merit Data Source
- **Source**: University of the Punjab Directorate of Students Affairs
- **Year**: 2024
- **Coverage**: All undergraduate programs across all faculties
- **Campuses**: Main, Gujranwala, Jhelum, Pothohar

## Updating Merit Data

To add merit data for a new year:

1. Extract merit percentages from the PDF
2. Add entries to `data/merit_data.csv` with columns:
   - Year
   - Faculty
   - Department
   - Program
   - Campus
   - Semester_Type
   - Merit_Percentage

3. Use the same format as existing entries
4. Restart the app

## Requirements

```
streamlit==1.40.0
pandas==2.1.4
fpdf2==2.8.1
openpyxl==3.11.0
```

## Deployment

### Deploy on Streamlit Cloud (Free)

1. **Push code to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Go to** [Streamlit Cloud](https://streamlit.io/cloud)

3. **Sign up** with your GitHub account

4. **Create new app**:
   - Select your repository
   - Select `app.py` as the main file
   - Click "Deploy"

5. **App is live!** Share the public URL with others

## Disclaimer

- This is a recommendation tool based on historical merit data
- Official admissions are handled by University of the Punjab
- Merit requirements may vary based on admission categories (Open Merit, PU Graduates, etc.)
- For official admissions information, visit: [www.pu.edu.pk](https://www.pu.edu.pk)

## Support

### University of the Punjab Contact
- **Email**: dsa@pu.edu.pk
- **Phone**: 042-99230181, 042-99232383
- **Address**: Q.A. Campus, Lahore

## License

This project is provided as-is for educational purposes.

## Contributing

To improve this app:
1. Add more years of merit data
2. Enhance UI/UX
3. Add more features (comparisons, statistics, etc.)
4. Report bugs and suggestions

---

**Created for**: Students of University of the Punjab  
**Last Updated**: May 2026  
**Status**: Active & Maintained
