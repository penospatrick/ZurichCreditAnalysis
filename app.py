"""
Credit File Scoring Web Application

A Streamlit app for analyzing credit reports and generating credit scores.
"""

import streamlit as st
import pandas as pd
import json
import tempfile
import os
from pathlib import Path

from creditfile.parse import get_file_details, parse_credit_report
from creditfile.normalize import normalize_credit_data
from creditfile.featurize import prepare_features
from creditfile.score import make_credit_score
from creditfile.utils import isna
from collections.abc import Iterable
from creditfile.assets.logo import ZURICH_LOGO_SVG


# Page configuration
st.set_page_config(
    page_title="Credit Score Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'processed_file' not in st.session_state:
    st.session_state.processed_file = None
if 'results' not in st.session_state:
    st.session_state.results = None

# Modern styling with larger fonts
st.markdown("""
    <style>
    /* Root styles */
    :root {
        --primary: #123b78;
        --primary-light: #2563eb;
        --secondary: #facc15;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }
    
    /* Main container */
    .main { 
        max-width: 1200px; 
        margin: 0 auto;
    }
    
    /* Typography - LARGER FONTS */
    h1, h2, h3, h4, h5, h6 {
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    
    h1 {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #123b78 0%, #2563eb 70%, #facc15 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.75rem !important;
    }
    
    h2 {
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        color: #1f2937 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        color: #374151 !important;
        margin-top: 1.5rem !important;
    }
    
    /* Body text */
    body, p, span, label, .stText, .stMarkdown {
        font-size: 1.2rem !important;
        line-height: 1.6 !important;
    }
    
    /* Cards and containers */
    .stMetric {
        background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%) !important;
        border: 1px solid #e5e7eb !important;
        padding: 2rem !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07) !important;
        transition: all 0.3s ease !important;
    }
    
    .stMetric:hover {
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12) !important;
        transform: translateY(-2px) !important;
    }
    
    .stMetricLabel {
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
    
    .stMetricValue {
        font-size: 3rem !important;
        font-weight: 700 !important;
    }
    
    .stMetricDelta {
        font-size: 1.1rem !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #e5e7eb !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 16px 24px !important;
        border-radius: 8px 8px 0 0 !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        color: #6b7280 !important;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #123b78 !important;
        background-color: transparent !important;
        border-bottom: 3px solid #facc15 !important;
    }
    
    /* File uploader */
    .stFileUploadDropzone {
        border: 2px dashed #d1d5db !important;
        border-radius: 12px !important;
        padding: 2.5rem !important;
        background: #fafafa !important;
    }
    
    .stFileUploadDropzone:hover {
        border-color: #2563eb !important;
        background: #eff6ff !important;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        padding: 1rem 2rem !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        border: none !important;
        background: linear-gradient(135deg, #123b78 0%, #2563eb 100%) !important;
        color: white !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(18, 59, 120, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(18, 59, 120, 0.4) !important;
    }
    
    /* Messages */
    .stSuccess {
        background-color: #ecfdf5 !important;
        border: 1px solid #10b981 !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
        color: #065f46 !important;
        font-size: 1.1rem !important;
    }
    
    .stWarning {
        background-color: #fffbeb !important;
        border: 1px solid #f59e0b !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
        color: #78350f !important;
        font-size: 1.1rem !important;
    }
    
    .stInfo {
        background-color: #eff6ff !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
        color: #1e40af !important;
        font-size: 1.1rem !important;
    }
    
    .stError {
        background-color: #fef2f2 !important;
        border: 1px solid #ef4444 !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
        color: #7f1d1d !important;
        font-size: 1.1rem !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 8px !important;
        border: 1px solid #e5e7eb !important;
        font-size: 1.1rem !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 8px !important;
        border: 1px solid #d1d5db !important;
        padding: 1rem !important;
        font-size: 1.1rem !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        border-radius: 8px !important;
        background: #f3f4f6 !important;
        border: 1px solid #e5e7eb !important;
        padding: 1.25rem !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: #e5e7eb !important;
    }
    
    /* Divider */
    hr {
        border-color: #e5e7eb !important;
        margin: 2rem 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Constants
ESSENTIAL_FIELDS = {
    'personal_data': [
        'name',
        'present_address',
        'present_address_tenure',
        'contact_no',
        'birthplace',
        'education',
        'parents_name',
        'parents_address',
        'date_applied',
        'unit_applied',
        'loan_amount',
        'loan_terms',
        'housing_status',
        'dob',
        'age',
        'marital_status',
        'n_children',
        'n_dependents',
        'dependent_ages'
    ],
    'income_analysis': {
        'summary': ['gross_income', 'monthly_amortization']
    },
    'officer_assessment': [
        'loan_purpose',
        'unit_payor',
        'unit_rider',
        'rider_license',
        'cell_signal_status',
        'prepared_by',
        'remarks'
    ]
}


# Utility functions
def is_missing(x):
    return isna(x) or (isinstance(x, Iterable) and all(isna(_) for _ in x))


def validate_fields(data, essential_fields=ESSENTIAL_FIELDS):
    """Check if the data contains all essential fields."""
    missing_fields = {}
    for k, v in essential_fields.items():
        subset = data.get(k, None)
        missing = None
        if isna(subset):
            missing_fields[k] = v
        elif isinstance(v, dict):
            missing = validate_fields(subset, v)
        elif isinstance(v, list):
            missing = [
                field for field in v if isna(subset.get(field, None))
            ]
        if missing:
            missing_fields[k] = missing
    return missing_fields


def format_missing_fields(missing_fields, level=0):
    """Format missing fields for display."""
    if not missing_fields:
        return "✅ All essential fields present"
    
    result = []
    for k, v in missing_fields.items():
        if isinstance(v, dict):
            result.append(f"  • {k}:")
            result.append(format_missing_fields(v, level + 1))
        elif isinstance(v, list):
            result.append(f"  • {k}: {', '.join(v)}")
        else:
            result.append(f"  • {k}")
    return "\n".join(result)


# Page layout
# Header with logo and title
st.html(f"""
    <div style="margin-bottom: 2rem; display: flex; align-items: center; gap: 1.5rem;">
        <div style="flex-shrink: 0;">
            {ZURICH_LOGO_SVG}
        </div>
        <div>
            <h1 style="margin: 0; font-size: 3.5rem; color: #001f3f;">Zurich Finance Corporation</h1>
            <h2 style="margin: 0.5rem 0 0 0; font-size: 1.8rem; color: #6b7280; font-weight: 500;">Credit Processing System</h2>
        </div>
    </div>
""")

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ About", unsafe_allow_html=True)
    st.markdown("""
        <div style="background: linear-gradient(135deg, #eff6ff 0%, #fffbea 100%); padding: 1.5rem; border-radius: 8px; border-left: 4px solid #facc15;">
            <p style="margin: 0; color: #1f2937; font-size: 1.1rem; font-weight: 700;"><strong>Smart Credit Analysis</strong></p>
            <p style="margin: 0.75rem 0 0 0; color: #6b7280; font-size: 1rem; line-height: 1.5;">
                This app processes credit reports and generates a credit score (1-100) based on:
            </p>
            <ul style="margin: 0.75rem 0 0 1.5rem; color: #6b7280; font-size: 1rem; line-height: 1.8;">
                <li>Personal information</li>
                <li>Income analysis</li>
                <li>Officer assessment</li>
                <li>Loan parameters</li>
            </ul>
            <p style="margin: 0.75rem 0 0 0; color: #6b7280; font-size: 1rem;"><strong>Supported format:</strong> Excel (.xlsx) files</p>
        </div>
    """, unsafe_allow_html=True)

# Main content
st.markdown("<h2 style='font-size: 2rem; margin-bottom: 1.5rem;'>📁 Upload Credit Report</h2>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose a credit report file", type=["xlsx"], label_visibility="collapsed")

if uploaded_file is not None:
    # Check if this is a new file or if we already have results
    current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    
    # Only process if it's a new file
    if st.session_state.processed_file != current_file_id:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name
        
        try:
            with st.spinner("Processing credit report..."):
                progress_bar = st.progress(0)
                
                # Step 1: Parse
                st.status("Parsing credit report...", state="running")
                progress_bar.progress(25)
                
                file_details = get_file_details(tmp_path)
                parsed = parse_credit_report(tmp_path)
                
                st.status("Parsing credit report...", state="complete")
                
                # Step 2: Normalize
                st.status("Normalizing data...", state="running")
                progress_bar.progress(50)
                
                normalized = normalize_credit_data(parsed)
                
                st.status("Normalizing data...", state="complete")
                
                # Step 3: Featurize
                st.status("Extracting features...", state="running")
                progress_bar.progress(75)
                
                features = prepare_features(normalized)
                
                st.status("Extracting features...", state="complete")
                
                # Step 4: Score
                st.status("Calculating credit score...", state="running")
                progress_bar.progress(90)
                
                missing_fields = validate_fields(normalized)
                missing_count = sum(1 for feature in features if isna(feature) or feature == -1)
                credit_score = make_credit_score(features)
                
                st.status("Complete!", state="complete")
                progress_bar.progress(100)
                
                # Determine rating
                if missing_count >= 5:
                    color = "⚠️"
                    rating = "Too many missing data fields"
                elif credit_score >= 75:
                    color = "🟢"
                    rating = "Excellent"
                elif credit_score >= 60:
                    color = "🟡"
                    rating = "Good"
                elif credit_score >= 40:
                    color = "🟠"
                    rating = "Fair"
                else:
                    color = "🔴"
                    rating = "Poor"
                
                # Store results in session state
                st.session_state.results = {
                    "credit_score": int(credit_score),
                    "rating": rating,
                    "color": color,
                    "missing_fields": missing_fields,
                    "missing_count": missing_count,
                    "normalized": normalized,
                    "uploaded_file_name": uploaded_file.name
                }
                st.session_state.processed_file = current_file_id
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.info("Please ensure your file is a valid credit report in Excel format.")
            with st.expander("Debug Information"):
                st.write(str(e))
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    # Display cached results if available
    if st.session_state.results is not None:
        results = st.session_state.results
        normalized = results["normalized"]
        credit_score = results["credit_score"]
        rating = results["rating"]
        color = results["color"]
        
        # Display results
        st.markdown('<div style="background: linear-gradient(135deg, #ecfdf5 0%, #fff9e6 100%); border: 1px solid #10b981; border-radius: 8px; padding: 1rem; margin-bottom: 2rem;"><span style="color: #065f46; font-weight: 600;">✓ Analysis completed successfully!</span></div>', unsafe_allow_html=True)
        
        # Credit Score Display - Modern Card
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%); border: 1px solid #e5e7eb; border-radius: 12px; padding: 2rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);">
                    <p style="color: #6b7280; font-size: 0.9rem; margin: 0 0 0.5rem 0; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Credit Score</p>
                    <div style="display: flex; align-items: baseline; gap: 1rem;">
                        <span style="font-size: 3.5rem; font-weight: 700; background: linear-gradient(135deg, #123b78 0%, #2563eb 70%, #facc15 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{credit_score if credit_score is not None else 'N/A'}</span>
                        <span style="font-size: 1.2rem; color: #6b7280;">/100</span>
                    </div>
                    <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;">
                        <span style="font-size: 1rem; font-weight: 600; color: #1f2937;">{rating}</span>
                        <span style="margin-left: 0.5rem; font-size: 1.5rem;">{color}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #eff6ff 0%, #fffbea 100%); border: 1px solid #bfdbfe; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);">
                    <p style="color: #123b78; font-size: 0.9rem; margin: 0 0 1rem 0; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Score Legend</p>
                    <div style="font-size: 0.9rem; color: #1f2937; line-height: 1.8;">
                        <div><span style="font-size: 1rem;">🟢</span> 75-100 Excellent</div>
                        <div><span style="font-size: 1rem;">🟡</span> 60-74 Good</div>
                        <div><span style="font-size: 1rem;">🟠</span> 40-59 Fair</div>
                        <div><span style="font-size: 1rem;">🔴</span> 0-39 Poor</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")  # Spacing
        
        # Tabs for detailed information
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📋 Personal Data", "💰 Income Analysis", "🏠 Assessment", "⚠️ Validation"]
        )
        
        with tab1:
            if "personal_data" in normalized:
                personal_df = pd.DataFrame(
                    list(normalized["personal_data"].items()),
                    columns=["Field", "Value"]
                )
                st.dataframe(personal_df, use_container_width=True, hide_index=True)
            else:
                st.info("📭 No personal data found")
        
        with tab2:
            if "income_analysis" in normalized:
                income_df = pd.DataFrame(
                    list(normalized["income_analysis"].items()),
                    columns=["Field", "Value"]
                )
                st.dataframe(income_df, use_container_width=True, hide_index=True)
            else:
                st.info("📭 No income data found")
        
        with tab3:
            if "credit_assessment" in normalized:
                assessment_df = pd.DataFrame(
                    list(normalized["credit_assessment"].items()),
                    columns=["Field", "Value"]
                )
                st.dataframe(assessment_df, use_container_width=True, hide_index=True)
            else:
                st.info("📭 No assessment data found")
        
        with tab4:
            missing_fields = validate_fields(normalized)
            
            if missing_fields:
                st.markdown('<div style="background: linear-gradient(135deg, #fffbeb 0%, #fff7e6 100%); border: 1px solid #f59e0b; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;"><span style="color: #92400e; font-weight: 600;">⚠️ Some essential fields are missing:</span></div>', unsafe_allow_html=True)
                st.code(format_missing_fields(missing_fields), language="text")
            else:
                st.markdown('<div style="background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%); border: 1px solid #10b981; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;"><span style="color: #065f46; font-weight: 600;">✓ All essential fields are present and valid</span></div>', unsafe_allow_html=True)
            
            # Show raw normalized data
            with st.expander("📋 View Raw Normalized Data"):
                st.json(
                    json.loads(
                        json.dumps(normalized, default=str)
                    )
                )
        
        # Download results
        st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
        st.markdown("### 📥 Export Results")
        col1, col2 = st.columns(2)
        
        with col1:
            results_json = dict(normalized)
            results_json["credit_score"] = credit_score
            st.download_button(
                label="📥 Download Validated Data (JSON)",
                data=json.dumps(results_json, indent=2, default=str),
                file_name=f"credit_score_{results['uploaded_file_name'].split('.')[0]}.json",
                mime="application/json"
            )
        
        with col2:
            # Export to CSV
            try:
                export_df = pd.DataFrame([results_json])
                st.download_button(
                    label="📥 Download Results (CSV)",
                    data=export_df.to_csv(index=False),
                    file_name=f"credit_score_{results['uploaded_file_name'].split('.')[0]}.csv",
                    mime="text/csv"
                )
            except:
                pass

else:
    st.info("👆 Upload a credit report Excel file to get started")
