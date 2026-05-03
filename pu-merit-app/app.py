import streamlit as st
import pandas as pd
from datetime import datetime
import io
from io import BytesIO
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

# Page Configuration
st.set_page_config(
    page_title="PU Merit Recommendation",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .safe-badge {
        background-color: #90EE90;
        color: black;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 12px;
    }
    .moderate-badge {
        background-color: #FFD700;
        color: black;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 12px;
    }
    .risky-badge {
        background-color: #FF6B6B;
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== DATA LOADING ====================
@st.cache_data
def load_merit_data():
    """Load and cache merit data from CSV"""
    try:
        df = pd.read_csv('data/merit_data.csv')
        # Remove rows where merit is 0.0 (missing data)
        df = df[df['Merit_Percentage'] > 0]
        return df
    except FileNotFoundError:
        st.error("❌ merit_data.csv not found in data/ folder")
        return None

# ==================== RECOMMENDATION ENGINE ====================
def categorize_difficulty(student_merit, program_merit):
    """
    Categorize program difficulty based on student merit vs program merit
    - Safe: Program cutoff 10%+ below student merit
    - Moderate: Program cutoff within 10% of student merit
    - Risky: Program cutoff above student merit but within 10%
    """
    margin = student_merit - program_merit
    
    if margin >= 10:
        return "Safe ✅", margin
    elif margin >= 0:
        return "Moderate ⚠️", margin
    elif margin >= -10:
        return "Risky ⚠️⚠️", margin
    else:
        return "Not Eligible ❌", margin

def get_recommendations(df, student_merit, selected_faculties, selected_campuses, 
                        selected_semesters, selected_years):
    """
    Get program recommendations based on student merit and filters
    """
    # Apply filters
    filtered_df = df[
        (df['Merit_Percentage'] <= student_merit) &
        (df['Faculty'].isin(selected_faculties)) &
        (df['Campus'].isin(selected_campuses)) &
        (df['Semester_Type'].isin(selected_semesters)) &
        (df['Year'].isin(selected_years))
    ].copy()
    
    # Calculate difficulty and margin for each program
    filtered_df['Difficulty'], filtered_df['Margin'] = zip(*filtered_df.apply(
        lambda row: categorize_difficulty(student_merit, row['Merit_Percentage']), 
        axis=1
    ))
    
    # Sort by difficulty (Safe first) and then by merit cutoff (highest first)
    difficulty_order = {'Safe ✅': 0, 'Moderate ⚠️': 1, 'Risky ⚠️⚠️': 2, 'Not Eligible ❌': 3}
    filtered_df['DifficultyOrder'] = filtered_df['Difficulty'].map(difficulty_order)
    filtered_df = filtered_df.sort_values(['DifficultyOrder', 'Merit_Percentage'], ascending=[True, False])
    filtered_df = filtered_df.drop('DifficultyOrder', axis=1)
    
    return filtered_df

def get_all_programs(df, student_merit, selected_years):
    """Get all eligible programs (no faculty/campus filter) for PDF export"""
    all_programs = df[
        (df['Merit_Percentage'] <= student_merit) &
        (df['Year'].isin(selected_years))
    ].copy()
    
    all_programs['Difficulty'], all_programs['Margin'] = zip(*all_programs.apply(
        lambda row: categorize_difficulty(student_merit, row['Merit_Percentage']), 
        axis=1
    ))
    
    difficulty_order = {'Safe ✅': 0, 'Moderate ⚠️': 1, 'Risky ⚠️⚠️': 2}
    all_programs['DifficultyOrder'] = all_programs['Difficulty'].map(difficulty_order)
    all_programs = all_programs.sort_values(['DifficultyOrder', 'Merit_Percentage'], ascending=[True, False])
    all_programs = all_programs.drop('DifficultyOrder', axis=1)
    
    return all_programs

# ==================== PDF EXPORT ====================
def generate_pdf(student_merit, year, recommendations_df):
    """Generate PDF report with recommendations using ReportLab"""
    if not HAS_REPORTLAB:
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=6,
        alignment=1  # Center
    )
    elements.append(Paragraph("University of the Punjab", title_style))
    elements.append(Paragraph("Merit-Based Program Recommendation Report", styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Student Info
    student_info_style = ParagraphStyle('StudentInfo', parent=styles['Normal'], fontSize=10)
    info_text = f"<b>Student Merit:</b> {student_merit}% | <b>Year:</b> {year} | <b>Generated:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}"
    elements.append(Paragraph(info_text, student_info_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # Summary Stats
    safe_count = len(recommendations_df[recommendations_df['Difficulty'] == 'Safe ✅'])
    moderate_count = len(recommendations_df[recommendations_df['Difficulty'] == 'Moderate ⚠️'])
    risky_count = len(recommendations_df[recommendations_df['Difficulty'] == 'Risky ⚠️⚠️'])
    
    summary_text = f"""
    <b>Summary Statistics:</b><br/>
    Safe Programs: {safe_count} | Moderate Programs: {moderate_count} | Risky Programs: {risky_count} | Total Eligible: {len(recommendations_df)}
    """
    elements.append(Paragraph(summary_text, student_info_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Table
    elements.append(Paragraph("<b>Eligible Programs</b>", styles['Heading3']))
    
    # Prepare table data
    table_data = [['Faculty', 'Program', 'Campus', 'Semester', 'Cutoff %', 'Difficulty']]
    
    for _, row in recommendations_df.iterrows():
        table_data.append([
            str(row['Faculty'])[:15],
            str(row['Program'])[:20],
            str(row['Campus'])[:12],
            str(row['Semester_Type'])[:12],
            f"{row['Merit_Percentage']:.1f}%",
            'Safe' if 'Safe' in row['Difficulty'] else 'Mod' if 'Moderate' in row['Difficulty'] else 'Risky'
        ])
    
    # Create table
    table = Table(table_data, colWidths=[1.2*inch, 1.5*inch, 1*inch, 1.2*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
    elements.append(Paragraph("This report is generated based on 2024 University of the Punjab merit data.", footer_style))
    elements.append(Paragraph("For official admissions information, visit: www.pu.edu.pk", footer_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ==================== MAIN APP ====================
# Title
st.title("🎓 PU Merit Recommendation System")
st.markdown("**Find your perfect program based on your merit score**")

# Load data
merit_df = load_merit_data()

if merit_df is not None:
    # ==================== SIDEBAR FILTERS ====================
    with st.sidebar:
        st.header("⚙️ Filters & Input")
        
        # Student Merit Input
        st.subheader("1️⃣ Your Merit")
        student_merit = st.number_input(
            "Enter your merit percentage (0-100):",
            min_value=0.0,
            max_value=100.0,
            value=70.0,
            step=0.5,
            help="Enter your entrance merit percentage or aggregate score as a percentage"
        )
        
        # Year Selection
        st.subheader("2️⃣ Year")
        available_years = sorted(merit_df['Year'].unique())
        selected_years = st.multiselect(
            "Select admission year(s):",
            available_years,
            default=[available_years[-1]]
        )
        
        # Faculty Selection
        st.subheader("3️⃣ Faculty")
        available_faculties = sorted(merit_df['Faculty'].unique())
        selected_faculties = st.multiselect(
            "Select faculty/ies (or leave empty for all):",
            available_faculties,
            default=available_faculties
        )
        if not selected_faculties:
            selected_faculties = available_faculties
        
        # Campus Selection
        st.subheader("4️⃣ Campus")
        available_campuses = sorted(merit_df['Campus'].unique())
        selected_campuses = st.multiselect(
            "Select campus/es (or leave empty for all):",
            available_campuses,
            default=available_campuses
        )
        if not selected_campuses:
            selected_campuses = available_campuses
        
        # Semester Type Selection
        st.subheader("5️⃣ Semester Type")
        available_semesters = sorted(merit_df['Semester_Type'].unique())
        selected_semesters = st.multiselect(
            "Select semester type(s):",
            available_semesters,
            default=available_semesters
        )
        if not selected_semesters:
            selected_semesters = available_semesters
    
    # ==================== MAIN CONTENT ====================
    # Get recommendations
    recommendations = get_recommendations(
        merit_df,
        student_merit,
        selected_faculties,
        selected_campuses,
        selected_semesters,
        selected_years
    )
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Eligible",
            len(recommendations),
            help="Total programs matching your merit and filters"
        )
    
    with col2:
        safe_count = len(recommendations[recommendations['Difficulty'] == 'Safe ✅'])
        st.metric(
            "Safe Programs",
            safe_count,
            help="Programs where cutoff is 10%+ below your merit"
        )
    
    with col3:
        moderate_count = len(recommendations[recommendations['Difficulty'] == 'Moderate ⚠️'])
        st.metric(
            "Moderate Programs",
            moderate_count,
            help="Programs where cutoff is within 10% of your merit"
        )
    
    with col4:
        risky_count = len(recommendations[recommendations['Difficulty'] == 'Risky ⚠️⚠️'])
        st.metric(
            "Risky Programs",
            risky_count,
            help="Programs slightly above your merit (competitive)"
        )
    
    # Results Display
    st.divider()
    st.subheader("📋 Recommended Programs")
    
    if len(recommendations) == 0:
        st.warning("❌ No programs found matching your criteria. Try adjusting your filters!")
    else:
        # Create display dataframe with formatted columns
        display_df = recommendations[[
            'Faculty', 'Department', 'Program', 'Campus', 'Semester_Type', 
            'Merit_Percentage', 'Margin', 'Difficulty'
        ]].copy()
        
        display_df.columns = ['Faculty', 'Department', 'Program', 'Campus', 'Semester Type', 'Cutoff %', 'Margin %', 'Difficulty']
        display_df['Cutoff %'] = display_df['Cutoff %'].round(2)
        display_df['Margin %'] = display_df['Margin %'].round(2)
        
        # Display as interactive table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Cutoff %": st.column_config.NumberColumn("Cutoff %", format="%.2f"),
                "Margin %": st.column_config.NumberColumn("Margin %", format="%.2f"),
                "Difficulty": st.column_config.TextColumn("Difficulty", width="medium")
            }
        )
        
        # PDF Export Section
        st.divider()
        st.subheader("📥 Download Report")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if HAS_REPORTLAB:
                st.markdown("Generate a detailed PDF report with all your recommendations.")
            else:
                st.warning("⚠️ PDF generation requires ReportLab library. CSV export available instead.")
        
        with col2:
            if HAS_REPORTLAB:
                # Generate PDF
                all_recommendations = get_all_programs(merit_df, student_merit, selected_years)
                pdf_buffer = generate_pdf(student_merit, selected_years[0], all_recommendations)
                
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"pu_merit_recommendation_{int(student_merit)}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                # Fallback: CSV export
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📊 Download CSV Report",
                    data=csv,
                    file_name=f"pu_merit_recommendation_{int(student_merit)}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    # Help Section
    st.divider()
    with st.expander("❓ How to use this app?"):
        st.markdown("""
        ### Instructions:
        
        1. **Enter Your Merit**: Input your entrance merit percentage (0-100%)
        2. **Select Year**: Choose the academic year you're applying for
        3. **Filter by Faculty**: Select specific faculties or leave empty for all
        4. **Filter by Campus**: Choose between Main, Gujranwala, Jhelum, or Pothohar
        5. **Filter by Semester**: Select Morning, Evening, or both
        6. **View Results**: See all eligible programs with difficulty levels
        7. **Download Report**: Get a PDF with all recommendations
        
        ### Difficulty Levels:
        - **Safe ✅**: Your merit is 10%+ above the program cutoff (highly likely admission)
        - **Moderate ⚠️**: Your merit is within 10% of the program cutoff (balanced choice)
        - **Risky ⚠️⚠️**: Program cutoff is slightly above your merit (competitive, but possible)
        
        ### Note:
        - Data is based on 2024 University of the Punjab merit list
        - This is a recommendation tool; official admissions are handled by the university
        - Merit requirements may vary based on category (Open Merit, PU Graduates, etc.)
        """)
    
    with st.expander("📞 Support & Information"):
        st.markdown("""
        ### University of the Punjab Contact:
        - **Email**: dsa@pu.edu.pk
        - **Phone**: 042-99230181, 042-99232383
        - **Website**: www.pu.edu.pk
        - **Address**: Q.A. Campus, Lahore
        
        ### About This App:
        - Created to help students understand merit-based program eligibility
        - Based on official merit lists from University of the Punjab
        - Last Updated: 2024
        """)
else:
    st.error("❌ Unable to load merit data. Please check that merit_data.csv exists in the data/ folder.")
