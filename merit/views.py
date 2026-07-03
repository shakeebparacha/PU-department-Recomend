from django.shortcuts import render
import pandas as pd
from django.conf import settings
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import os
from pathlib import Path


def load_merit_data():
    """Load merit data from CSV file"""
    try:
        # List of possible CSV file names and paths to try
        candidate_paths = [
            settings.DATA_FILE_PATH,
            settings.BASE_DIR / 'data' / 'merit_data.csv',
            settings.BASE_DIR / 'data' / '2024 merit.csv',
            settings.BASE_DIR / 'pu-merit-app' / 'data' / 'merit_data.csv',
            settings.BASE_DIR / 'pu-merit-app' / 'data' / '2024 merit.csv',
            Path('./data/merit_data.csv'),
            Path('./data/2024 merit.csv'),
            Path('../data/merit_data.csv'),
            Path('../data/2024 merit.csv'),
        ]
        
        # Also search for any CSV file in the data directory
        for data_search_path in [settings.BASE_DIR / 'data', settings.BASE_DIR / 'pu-merit-app' / 'data', Path('./data'), Path('../data')]:
            try:
                if data_search_path.exists() and data_search_path.is_dir():
                    for csv_file in data_search_path.glob('*.csv'):
                        if csv_file not in candidate_paths:
                            candidate_paths.append(csv_file)
            except:
                pass
        
        for path in candidate_paths:
            if path and os.path.exists(path):
                try:
                    df = pd.read_csv(path)
                    merit_col = 'Merit_Percentage' if 'Merit_Percentage' in df.columns else 'merit_percentage'
                    if merit_col in df.columns:
                        df = df[df[merit_col] > 0]
                    print(f"Successfully loaded merit data from: {path}")
                    return df
                except Exception as e:
                    print(f"Error loading data from {path}: {e}")
                    continue
        
        print("No valid CSV file found in candidate paths")
        print(f"BASE_DIR: {settings.BASE_DIR}")
        print(f"Available candidate paths checked: {[str(p) for p in candidate_paths[:5]]}")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def get_column_name(df, candidates):
    for name in candidates:
        if name in df.columns:
            return name
    return None


def get_filter_options():
    """Extract unique values for filters from data"""
    df = load_merit_data()
    if df is None:
        return {
            'faculties': [],
            'departments': [],
            'programs': [],
            'campuses': [],
            'semesters': [],
            'years': []
        }
    
    faculty_col = get_column_name(df, ['Faculty', 'faculty'])
    department_col = get_column_name(df, ['Department', 'department'])
    program_col = get_column_name(df, ['Program', 'program'])
    campus_col = get_column_name(df, ['Campus', 'campus'])
    semester_col = get_column_name(df, ['Semester_Type', 'Semester', 'semester'])
    year_col = get_column_name(df, ['Year', 'year'])

    def unique_values(col_name):
        if not col_name:
            return []
        return sorted(df[col_name].dropna().unique().tolist())
    
    return {
        'faculties': unique_values(faculty_col),
        'departments': unique_values(department_col),
        'programs': unique_values(program_col),
        'campuses': unique_values(campus_col),
        'semesters': unique_values(semester_col),
        'years': unique_values(year_col)
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


def generate_pdf_report(student_merit, year_label, recommendations_df):
    if recommendations_df is None or recommendations_df.empty:
        return None

    reports_dir = settings.MEDIA_ROOT / 'reports'
    os.makedirs(reports_dir, exist_ok=True)

    merit_tag = str(student_merit).replace('.', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"pu_merit_recommendations_{merit_tag}_{timestamp}.pdf"
    output_path = reports_dir / filename

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#0d2d47'),
        spaceAfter=6,
        alignment=1
    )
    elements.append(Paragraph("University of the Punjab", title_style))
    elements.append(Paragraph("Merit-Based Program Recommendation Report", styles['Heading2']))
    elements.append(Spacer(1, 0.2 * inch))

    info_style = ParagraphStyle('ReportInfo', parent=styles['Normal'], fontSize=10)
    info_text = (
        f"<b>Student Merit:</b> {student_merit}% | "
        f"<b>Year:</b> {year_label} | "
        f"<b>Generated:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}"
    )
    elements.append(Paragraph(info_text, info_style))
    elements.append(Spacer(1, 0.15 * inch))

    table_data = [['Faculty', 'Department', 'Program', 'Campus', 'Semester', 'Cutoff %', 'Category']]
    for _, row in recommendations_df.iterrows():
        table_data.append([
            str(row.get('Faculty', ''))[:18],
            str(row.get('Department', ''))[:20],
            str(row.get('Program', ''))[:20],
            str(row.get('Campus', ''))[:12],
            str(row.get('Semester', row.get('Semester_Type', '')))[:14],
            f"{row.get('Merit_Percentage', 0):.1f}%",
            str(row.get('Category', ''))
        ])

    table = Table(table_data, colWidths=[1.2 * inch, 1.5 * inch, 1.5 * inch, 1.0 * inch, 1.2 * inch, 0.8 * inch, 1.0 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d2d47')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f4f4f4')])
    ]))

    elements.append(table)
    doc.build(elements)

    with open(output_path, 'wb') as output_file:
        output_file.write(buffer.getvalue())

    return f"{settings.MEDIA_URL}reports/{filename}"


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
    pdf_url = None
    metrics = {
        'total': 0,
        'safe': 0,
        'moderate': 0,
        'risky': 0,
        'not_eligible': 0,
    }

    selected_faculties = filter_options.get('faculties', [])
    selected_departments = filter_options.get('departments', [])
    selected_programs = filter_options.get('programs', [])
    selected_campuses = filter_options.get('campuses', [])
    # ---- default semester filter (only first‑semester options) ----
    default_semester_names = [
        '1st Semester Morning',
        '1st Semester Evening/Replica/Self Support',
       
    ]
    default_selected_semesters = [
        sem for sem in filter_options.get('semesters', []) if sem in default_semester_names
    ]
    selected_semesters = default_selected_semesters
    selected_years = [str(year) for year in filter_options.get('years', [])]
    
    # Check for GET parameter (from merit calculator)
    if request.method == 'GET' and 'merit' in request.GET:
        try:
            student_merit = float(request.GET.get('merit', 0))
            # Auto-trigger the calculation with the passed merit value
            if student_merit > 0:
                request.method = 'POST'  # Treat as POST for processing
        except ValueError:
            student_merit = None
    
    if request.method == 'POST' or student_merit:
        try:
            # Get merit from POST if it's a POST request, otherwise use already extracted GET value
            if request.method == 'POST' and not student_merit:
                student_merit = float(request.POST.get('student_merit', 0))
            
            # Get selected filters
            selected_faculties = request.POST.getlist('faculties') if request.method == 'POST' else filter_options.get('faculties', [])
            selected_departments = request.POST.getlist('departments') if request.method == 'POST' else filter_options.get('departments', [])
            selected_programs = request.POST.getlist('programs') if request.method == 'POST' else filter_options.get('programs', [])
            selected_campuses = request.POST.getlist('campuses') if request.method == 'POST' else filter_options.get('campuses', [])
            if request.method == 'POST':
                selected_semesters = request.POST.getlist('semesters')
                # If the form was auto‑submitted (no semesters sent), keep the defaults
                if not selected_semesters:
                    selected_semesters = default_selected_semesters
            else:
                selected_semesters = default_selected_semesters
            selected_years = request.POST.getlist('years') if request.method == 'POST' else [str(year) for year in filter_options.get('years', [])]
            
            if not selected_faculties:
                selected_faculties = filter_options.get('faculties', [])
            if not selected_departments:
                selected_departments = filter_options.get('departments', [])
            if not selected_programs:
                selected_programs = filter_options.get('programs', [])
            if not selected_campuses:
                selected_campuses = filter_options.get('campuses', [])
            if not selected_semesters:
                selected_semesters = filter_options.get('semesters', [])
            if not selected_years:
                selected_years = [str(year) for year in filter_options.get('years', [])]
            
            if student_merit <= 0:
                error_message = "Please enter a valid merit percentage (greater than 0)"
            else:
                df = load_merit_data()
                if df is not None:
                    faculty_col = get_column_name(df, ['Faculty', 'faculty'])
                    department_col = get_column_name(df, ['Department', 'department'])
                    program_col = get_column_name(df, ['Program', 'program'])
                    campus_col = get_column_name(df, ['Campus', 'campus'])
                    semester_col = get_column_name(df, ['Semester_Type', 'Semester', 'semester'])
                    year_col = get_column_name(df, ['Year', 'year'])
                    merit_col = get_column_name(df, ['Merit_Percentage', 'merit_percentage'])
                    stream_col = get_column_name(df, ['Sci / Arts', 'Sci/Arts', 'Stream', 'stream'])
                    
                    # Apply filters (show all suggestions, including not eligible)
                    filtered_df = df.copy()
                    
                    filtered_df = filtered_df[filtered_df[faculty_col].isin(selected_faculties)]
                    if department_col:
                        filtered_df = filtered_df[filtered_df[department_col].isin(selected_departments)]
                    if program_col:
                        filtered_df = filtered_df[filtered_df[program_col].isin(selected_programs)]
                    filtered_df = filtered_df[filtered_df[campus_col].isin(selected_campuses)]
                    filtered_df = filtered_df[filtered_df[semester_col].isin(selected_semesters)]
                    year_values = selected_years
                    if year_col:
                        try:
                            year_values = [int(year) for year in selected_years]
                        except ValueError:
                            year_values = selected_years
                        filtered_df = filtered_df[filtered_df[year_col].isin(year_values)]
                    
                    if merit_col:
                        difficulty_data = filtered_df[merit_col].apply(
                            lambda merit_value: categorize_difficulty(student_merit, merit_value)
                        )
                        filtered_df[['Category', 'Badge', 'Margin']] = pd.DataFrame(
                            difficulty_data.tolist(),
                            index=filtered_df.index
                        )
                        difficulty_order = {
                            'Safe': 0,
                            'Moderate': 1,
                            'Risky': 2,
                            'Not Eligible': 3
                        }
                        filtered_df['DifficultyOrder'] = filtered_df['Category'].map(difficulty_order)
                        filtered_df = filtered_df.sort_values(
                            ['DifficultyOrder', merit_col],
                            ascending=[True, False]
                        )
                        filtered_df = filtered_df.drop('DifficultyOrder', axis=1)
                    
                    # Prepare recommendations
                    for idx, row in filtered_df.iterrows():
                        recommendations.append({
                            'faculty': row[faculty_col] if faculty_col else '',
                            'department': row[department_col] if department_col else '',
                            'program': row[program_col] if program_col else '',
                            'merit': row[merit_col] if merit_col else '',
                            'campus': row[campus_col] if campus_col else '',
                            'semester': row[semester_col] if semester_col else '',
                            'year': row[year_col] if year_col else '',
                            'stream': row[stream_col].lower() if stream_col and row[stream_col] else 'science',
                            'category': row.get('Category', ''),
                            'badge': row.get('Badge', ''),
                            'margin': f"{row.get('Margin', 0):.1f}%"
                        })
                    
                    if not filtered_df.empty:
                        metrics['total'] = len(filtered_df)
                        metrics['safe'] = int((filtered_df['Category'] == 'Safe').sum())
                        metrics['moderate'] = int((filtered_df['Category'] == 'Moderate').sum())
                        metrics['risky'] = int((filtered_df['Category'] == 'Risky').sum())
                        metrics['not_eligible'] = int((filtered_df['Category'] == 'Not Eligible').sum())
                        year_label = ', '.join(selected_years) if selected_years else 'All'
                        pdf_url = generate_pdf_report(student_merit, year_label, filtered_df)

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
        'student_merit': round(student_merit, 2) if student_merit else None,
        'error_message': error_message,
        'pdf_url': pdf_url,
        'metrics': metrics,
        'selected_faculties': selected_faculties,
        'selected_departments': selected_departments,
        'selected_programs': selected_programs,
        'selected_campuses': selected_campuses,
        'selected_semesters': selected_semesters,
        'selected_years': selected_years,
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


def debug_csv_status(request):
    """Debug endpoint to check CSV loading status"""
    import json
    from django.http import JsonResponse
    from django.conf import settings
    
    debug_info = {
        "status": "checking",
        "base_dir": str(settings.BASE_DIR),
        "data_file_path": str(settings.DATA_FILE_PATH),
        "csv_files": [],
        "csv_loaded": False,
        "row_count": 0,
        "error": None
    }
    
    try:
        # Check what CSV files exist
        data_dir = settings.BASE_DIR / 'data'
        if data_dir.exists():
            for csv_file in data_dir.glob('*.csv'):
                debug_info["csv_files"].append(str(csv_file))
        
        # Try loading
        df = load_merit_data()
        if df is not None:
            debug_info["csv_loaded"] = True
            debug_info["row_count"] = len(df)
            debug_info["status"] = "success"
        else:
            debug_info["status"] = "error"
            debug_info["error"] = "load_merit_data() returned None"
    except Exception as e:
        debug_info["status"] = "error"
        debug_info["error"] = str(e)
    
    return JsonResponse(debug_info)
