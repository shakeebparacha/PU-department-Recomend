import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import io

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
    """Generate PDF report with recommendations"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Header
    pdf.cell(0, 15, "University of the Punjab", ln=True, align="C")
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Merit-Based Program Recommendation Report", ln=True, align="C")
    
    # Student Info
    pdf.set_font("Arial", "", 10)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 8, "Student Merit:")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"{student_merit}%", ln=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 8, "Year:")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, str(year), ln=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 8, "Generated:")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, datetime.now().strftime("%d-%m-%Y %H:%M"), ln=True)
    
    # Summary Stats
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, "Summary Statistics", ln=True)
    pdf.set_font("Arial", "", 9)
    
    safe_count = len(recommendations_df[recommendations_df['Difficulty'] == 'Safe ✅'])
    moderate_count = len(recommendations_df[recommendations_df['Difficulty'] == 'Moderate ⚠️'])
    risky_count = len(recommendations_df[recommendations_df['Difficulty'] == 'Risky ⚠️⚠️'])
    
    pdf.cell(50, 7, f"Safe Programs: {safe_count}")
    pdf.cell(50, 7, f"Moderate Programs: {moderate_count}", ln=True)
    pdf.cell(50, 7, f"Risky Programs: {risky_count}", ln=True)
    pdf.cell(50, 7, f"Total Eligible: {len(recommendations_df)}", ln=True)
    
    # Programs Table
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, "Eligible Programs", ln=True)
    pdf.set_font("Arial", "B", 8)
    
    # Table header
    col_widths = [25, 35, 20, 20, 20, 20]
    headers = ["Faculty", "Program", "Campus", "Semester", "Cutoff %", "Difficulty"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1, align="C")
    pdf.ln()
    
    # Table data
    pdf.set_font("Arial", "", 7)
    for _, row in recommendations_df.iterrows():
        pdf.cell(col_widths[0], 7, str(row['Faculty'])[:20], border=1)
        pdf.cell(col_widths[1], 7, str(row['Program'])[:30], border=1)
        pdf.cell(col_widths[2], 7, str(row['Campus'])[:15], border=1)
        pdf.cell(col_widths[3], 7, str(row['Semester_Type'])[:15], border=1)
        pdf.cell(col_widths[4], 7, f"{row['Merit_Percentage']:.1f}%", border=1, align="C")
        difficulty_short = "Safe" if "Safe" in row['Difficulty'] else "Mod" if "Moderate" in row['Difficulty'] else "Risky"
        pdf.cell(col_widths[5], 7, difficulty_short, border=1, align="C")
        pdf.ln()
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", "", 8)
    pdf.cell(0, 5, "This report is generated based on 2024 University of the Punjab merit data.", ln=True)
    pdf.cell(0, 5, "For official admissions information, visit: www.pu.edu.pk", ln=True)
    
    return io.BytesIO(pdf.output().encode('latin-1'))

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
            st.markdown("Generate a detailed PDF report with all your recommendations.")
        
        with col2:
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
