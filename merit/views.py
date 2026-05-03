from django.shortcuts import render
import pandas as pd
from django.conf import settings
import os


def load_merit_data():
    """Load merit data from CSV file"""
    try:
        if os.path.exists(settings.DATA_FILE_PATH):
            df = pd.read_csv(settings.DATA_FILE_PATH)
            # Remove rows where merit is 0.0 (missing data)
            df = df[df['Merit_Percentage'] > 0]
            return df
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def get_filter_options():
    """Extract unique values for filters from data"""
    df = load_merit_data()
    if df is None:
        return {
            'faculties': [],
            'campuses': [],
            'semesters': [],
            'years': []
        }
    
    # Handle column name variations
    faculty_col = 'Faculty' if 'Faculty' in df.columns else 'faculty'
    campus_col = 'Campus' if 'Campus' in df.columns else 'campus'
    semester_col = 'Semester' if 'Semester' in df.columns else 'semester'
    year_col = 'Year' if 'Year' in df.columns else 'year'
    
    return {
        'faculties': sorted(df[faculty_col].unique().tolist()),
        'campuses': sorted(df[campus_col].unique().tolist()),
        'semesters': sorted(df[semester_col].unique().tolist()),
        'years': sorted(df[year_col].unique().tolist())
    }


def categorize_difficulty(student_merit, program_merit):
    """
    Categorize program difficulty based on student merit vs program merit
    - Safe: Program cutoff 10%+ below student merit
    - Moderate: Program cutoff within 10% of student merit
    - Risky: Program cutoff above student merit but within 10%
    """
    margin = student_merit - program_merit
    
    if margin >= 10:
        category = "Safe"
        badge = "success"
    elif margin >= 0:
        category = "Moderate"
        badge = "warning"
    elif margin >= -10:
        category = "Risky"
        badge = "danger"
    else:
        category = "Not Eligible"
        badge = "dark"
    
    return category, badge, margin


def home(request):
    """Home page view"""
    context = {
        'page_title': 'Home'
    }
    return render(request, 'merit/home.html', context)


def merit_calculator(request):
    """New PU BS Merit Calculator (Type 1 and Type 2)"""
    context = {
        'page_title': 'Merit Calculator',
    }
    return render(request, 'merit/merit_calculator.html', context)


def program_finder(request):
    """Program finder - find programs based on your merit"""
    filter_options = get_filter_options()
    recommendations = []
    student_merit = None
    error_message = None
    
    if request.method == 'POST':
        try:
            student_merit = float(request.POST.get('student_merit', 0))
            
            # Get selected filters
            selected_faculties = request.POST.getlist('faculties')
            selected_campuses = request.POST.getlist('campuses')
            selected_semesters = request.POST.getlist('semesters')
            selected_years = request.POST.getlist('years')
            
            if student_merit <= 0:
                error_message = "Please enter a valid merit percentage (greater than 0)"
            else:
                df = load_merit_data()
                if df is not None:
                    # Handle column name variations
                    faculty_col = 'Faculty' if 'Faculty' in df.columns else 'faculty'
                    campus_col = 'Campus' if 'Campus' in df.columns else 'campus'
                    semester_col = 'Semester' if 'Semester' in df.columns else 'semester'
                    year_col = 'Year' if 'Year' in df.columns else 'year'
                    merit_col = 'Merit_Percentage' if 'Merit_Percentage' in df.columns else 'merit_percentage'
                    program_col = 'Program' if 'Program' in df.columns else 'program'
                    
                    # Apply filters
                    filtered_df = df[df[merit_col] <= student_merit]
                    
                    if selected_faculties:
                        filtered_df = filtered_df[filtered_df[faculty_col].isin(selected_faculties)]
                    if selected_campuses:
                        filtered_df = filtered_df[filtered_df[campus_col].isin(selected_campuses)]
                    if selected_semesters:
                        filtered_df = filtered_df[filtered_df[semester_col].isin(selected_semesters)]
                    if selected_years:
                        filtered_df = filtered_df[filtered_df[year_col].isin(map(int, selected_years))]
                    
                    # Sort by merit percentage descending
                    filtered_df = filtered_df.sort_values(merit_col, ascending=False)
                    
                    # Prepare recommendations
                    for idx, row in filtered_df.iterrows():
                        category, badge, margin = categorize_difficulty(student_merit, row[merit_col])
                        recommendations.append({
                            'faculty': row[faculty_col],
                            'program': row[program_col],
                            'merit': row[merit_col],
                            'campus': row[campus_col],
                            'semester': row[semester_col],
                            'year': row[year_col],
                            'category': category,
                            'badge': badge,
                            'margin': f"{margin:.1f}%"
                        })
                    
                    if not recommendations:
                        error_message = "No programs found matching your merit and selected filters."
        
        except ValueError:
            error_message = "Please enter a valid merit percentage."
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
    
    context = {
        'page_title': 'Program Finder',
        'filter_options': filter_options,
        'recommendations': recommendations,
        'student_merit': student_merit,
        'error_message': error_message,
    }
    return render(request, 'merit/program_finder.html', context)


def recommendations(request):
    """Department recommendations page"""
    filter_options = get_filter_options()
    
    context = {
        'page_title': 'Department Recommendations',
        'filter_options': filter_options,
    }
    return render(request, 'merit/recommendations.html', context)
