import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
from utils.data_processing import load_csv, filter_data_multi

# Set page configuration
st.set_page_config(
    page_title="CSV Data Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS for better styling
def local_css():
    st.markdown("""
    <style>
    .main {
        padding: 3rem 1rem;
    }
    h1 {
        color: #2E86C1;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    h2 {
        color: #1F618D;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    .stButton>button {
        background-color: #2874A6;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #1A5276;
        border-color: #1A5276;
    }
    .reportview-container .main .block-container {
        padding-top: 1rem;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    div.stNumberInput > div > div > input {
        border-radius: 5px;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Apply custom styling
    local_css()
    
    # App header with logo
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("# 📊 R & D Tool")
    
    st.markdown("---")
    
    # File uploader with better styling
    # st.markdown("### Upload Your Data")
    # uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    # Load the CSV file
    df = load_csv('./Data/Master.csv')
    
    # Initialize filtered dataframe
    filtered_df = df.copy()
    
    # Initialize session state for the input value if it doesn't exist
    if 'input_value' not in st.session_state:
        st.session_state.input_value = 0.0

    # Dictionary to store filter selections
    filters = {}
    
    # Filter controls - below the chart
    st.subheader("Filter Options")
    
    # Create a container with a light background for filters
    filter_container = st.container()
    with filter_container:
        
        # Create two columns for the filter buttons
        st.markdown("</div>", unsafe_allow_html=True)  # Close the background div
    
    col1, col2, col3 = st.columns(3)
    
    # Filters for Material Code
    with col1:
        st.write("Filter by Machine ID")
        unique_mach_codes = df['MachineId'].unique().tolist()
        selected_mach_codes = st.multiselect(
            f"Select Machine Id values",
            unique_mach_codes,
            default=[]
        )
        filters["MachineId"] = selected_mach_codes
        filtered_df = filter_data_multi(df, filters)

    # Filters for Material Description
    with col2:        
        st.write("Filter by Material Description")
        unique_mat_desc = filtered_df['MaterialDesc'].unique().tolist()
        selected_mat_desc = st.multiselect(
            f"Select Material Description values",
            unique_mat_desc,
            default=[]
        )
        filters["MaterialDesc"] = selected_mat_desc
        filtered_df = filter_data_multi(df, filters)

        # Filters for Material Description
    with col3:        
        st.write("Filter by Dimension Description")
        unique_dim_desc = filtered_df['DimensionDesc'].unique().tolist()
        selected_dim_desc = st.multiselect(
            f"Select Dimension Description values",
            unique_dim_desc,
            default=[]
        )
        filters["DimensionDesc"] = selected_dim_desc
        filtered_df = filter_data_multi(df, filters)
    
    # Display the filtered dataframe
    st.subheader("Data Table")
    st.dataframe(filtered_df, use_container_width=True, height=400)
    
    # Show number of records after filtering with better styling
    st.markdown(f"""
    <div style="background-color: #EBF5FB; padding: 10px; border-radius: 5px; margin: 10px 0px;">
        <span style="color: #2874A6; font-weight: 600;">📋 Showing {len(filtered_df)} of {len(df)} records</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Arithmetic operations - a single line with text input and a button
    st.subheader("Input Tolerance")
    
    # Create a single column for the input box
    USL = filtered_df['USL'].unique()[0]
    LSL = filtered_df['LSL'].unique()[0]
    Tolerance = (USL - LSL)
    value = st.number_input("Tolerance", value=Tolerance, step=0.01, format="%.4f", min_value=0.0)

    # Create two columns for displaying data
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.subheader("Actual Measurements")
        # Display standard deviation and other actual measurements
        if 'MeasValue' in filtered_df.columns:
            std_dev = filtered_df['MeasValue'].std()
            
            # Get CP and CPK from filtered data if they exist
            cp = filtered_df['Cp'].mean() if 'Cp' in filtered_df.columns else "N/A"
            cpk = filtered_df['Cpk'].mean() if 'Cpk' in filtered_df.columns else "N/A"
            
            # Create a styled container for actual measurements
            st.markdown(f"""
            <div style="background-color: #F8F9F9; padding: 15px; border-radius: 5px; border-left: 5px solid #2E86C1; margin: 10px 0px;">
                <p style="font-size: 1.1rem; font-weight: 600; color: #2C3E50;">Std Dev: {std_dev:.4f}</p>
                <p style="font-size: 1.1rem; font-weight: 600; color: #2C3E50;">Cp: {cp if isinstance(cp, str) else cp:.4f}</p>
                <p style="font-size: 1.1rem; font-weight: 600; color: #2C3E50;">Cpk: {cpk if isinstance(cpk, str) else cpk:.4f}</p>
                <p style="font-size: 1.1rem; font-weight: 600; color: #2C3E50;">Gage R&R: {filtered_df['Gage_RR'].unique()[0]:.2f}</p>
                <p style="font-size: 1.1rem; font-weight: 600; color: #2C3E50;">Tolerance: {Tolerance:.2f}</p>
            </div>
            """, unsafe_allow_html=True)

            st.subheader("Suggested Measurements")
            # Calculate optimal tolerance
            from utils.data_processing import Predict_Best_Tolerance_based_on_Material
            optimal_result = Predict_Best_Tolerance_based_on_Material(filtered_df)
            
            if optimal_result["success"]:
                st.markdown(f"""
                <div style="background-color: #E8F6F3; padding: 15px; border-radius: 5px; border-left: 5px solid #16A085; margin: 10px 0px;">
                    <h3 style="color: #16A085; margin-top: 0;">Recommended Optimal Tolerance:</h3>
                    <p style="font-size: 1.1rem; font-weight: 600; color: #2C3E50;">Recommended Scenario: {optimal_result["recommended_scenario"]}</p>
                    <p style="font-size: 1.1rem; font-weight: 600; color: #2C3E50;">Tolerance: {optimal_result["best_tolerance"]:.4f}</p>
                    <p style="font-size: 0.9rem; color: #566573;">This tolerance would achieve:</p>
                    <p style="font-size: 0.9rem; color: #566573;">• Cp = {optimal_result["resulting_cp"]:.2f}</p>
                    <p style="font-size: 0.9rem; color: #566573;">• Cpk = {optimal_result["resulting_cpk"]:.2f}</p>
                    <p style="font-size: 0.9rem; color: #566573;">• Gage R&R = {optimal_result["resulting_gage_rr"]:.2f}%</p>
                    <p style="font-size: 0.9rem; color: #566573;">• New LSL = {optimal_result["new_lsl"]:.4f}</p>
                    <p style="font-size: 0.9rem; color: #566573;">• New USL = {optimal_result["new_usl"]:.4f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create an expandable section for all scenarios
                with st.expander("View All Tolerance Scenarios"):
                    # Create a table for all the scenarios
                    scenario_data = []
                    for idx, scenario in enumerate(optimal_result["all_scenarios"]):
                        scenario_data.append({
                            "Scenario": scenario["name"],
                            "Tolerance": f"{scenario['tolerance']:.4f}",
                            "Cp": f"{scenario['cp']:.2f}",
                            "Cpk": f"{scenario['cpk']:.2f}",
                            "Gage R&R (%)": f"{scenario['gage_rr']:.2f}",
                            "LSL": f"{scenario['lsl']:.4f}",
                            "USL": f"{scenario['usl']:.4f}"
                        })
                    
                    # Display as a dataframe
                    st.dataframe(scenario_data, use_container_width=True)
                    
                    st.markdown("""
                    ### Scenario Details:
                    
                    - **Minimum Acceptable Tolerance (Cp = 1.0)**: Meets the minimum requirement for process capability
                    - **Good Quality Tolerance (Cp = 1.33)**: Represents a good balance of process capability
                    - **High Quality Tolerance (Cp = 1.67)**: High-quality process suitable for critical applications
                    - **Excellent Measurement System (Gage R&R = 10%)**: Prioritizes measurement system quality
                    
                    The recommended scenario balances process capability (Cp/Cpk) with measurement system quality (Gage R&R).
                    """)
            else:
                st.markdown(f"""
                <div style="background-color: #FDEDEC; padding: 15px; border-radius: 5px; border-left: 5px solid #C0392B; margin: 10px 0px;">
                    <h3 style="color: #C0392B; margin-top: 0;">Tolerance Optimization:</h3>
                    <p style="font-size: 1.0rem; color: #2C3E50;">{optimal_result.get("message", "Could not calculate optimal tolerance.")}</p>
                </div>
                """, unsafe_allow_html=True)

    with right_col:
        st.subheader("Forecast CP and Gage R&R")
        result_df = value / (6 * std_dev)
        
        st.markdown(f"""
        <div style="background-color: #E8F8F5; padding: 9px; border-radius: 5px; border-left: 5px solid #1ABC9C; margin: 5px 0px;">
            <h3 style="color: #16A085; margin-top: 0;">Forecasted CP:</h3>
            <p style="font-size: 1.2rem; font-weight: 600; color: #2C3E50;">CP: {result_df:.4f}</p>
        </div>
        """, unsafe_allow_html=True)


        # Get the Gage R&R value from the filtered data
        gage_rr_value = filtered_df['Gage_RR'].unique()[0]
        Forecast_GRR = ((gage_rr_value * Tolerance) / value)

        st.markdown(f"""
        <div style="background-color: #EDE7F6; padding: 9px; border-radius: 5px; border-left: 5px solid #7B1FA2; margin: 5px 0px;">
            <h3 style="color: #6A1B9A; margin-top: 0;">Forecasted Gage R&R:</h3>
            <p style="font-size: 1.2rem; font-weight: 600; color: #4A148C;">Forecast Gage R&R: {Forecast_GRR:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
        
if __name__ == "__main__":
    main()