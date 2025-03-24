import streamlit as st
import pandas as pd
import os
from io import BytesIO

# -------- Set page config -------- #
st.set_page_config(
    page_title="💿 CSV to Excel and Excel to CSV Converter",
    page_icon=":shark:",
    layout="wide"
)

# -------- Custom CSS for enhanced UI -------- #
st.markdown("""
    <style>
        .main {
            background-color: #f5f5f5;
        }
        .stButton>button {
            background-color: #007BFF;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 0.5rem 1rem;
            font-size: 1rem;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        .header {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
            color: #333;
        }
        .subheader {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #444;
        }
    </style>
    """, unsafe_allow_html=True)

# -------- Set title -------- #
st.markdown("<h1 class='header'>💿 File Converter</h1>", unsafe_allow_html=True)
st.write("Transform your CSV and Excel files with built-in data cleaning, visualization, and conversion options—all in one elegant solution.")

# -------- File Upload -------- #
uploaded_files = st.file_uploader("Upload your file (CSV or Excel)", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for i, file in enumerate(uploaded_files):
        # Create a unique key base for each file using loop index and file name
        key_base = f"{i}_{file.name}"
        file_ext = os.path.splitext(file.name)[-1].lower()
        # Read file based on its type
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        st.markdown(f"### File: {file.name}")
        st.write(f"**File Size:** {file.size/1024:.2f} KB")
        st.write("Preview of the data:")
        st.dataframe(df.head())

        # -------- Data Cleaning Options -------- #
        st.markdown("#### Data Cleaning Options")
        if st.checkbox(f"Clean data for {file.name}", key=f"clean_data_{key_base}"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Remove duplicates in {file.name}", key=f"remove_duplicates_{key_base}"):
                    initial_rows = df.shape[0]
                    df.drop_duplicates(inplace=True)
                    st.success(f"Duplicates removed! ({initial_rows - df.shape[0]} rows dropped)")
            with col2:
                if st.button(f"Fill missing values in {file.name}", key=f"fill_missing_{key_base}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    if not numeric_cols.empty:
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.success("Missing numeric values filled with column means.")
                    else:
                        st.info("No numeric columns found to fill missing values.")

        # -------- Column Selection -------- #
        st.markdown("#### Column Selection")
        selected_columns = st.multiselect(
            f"Select columns to keep for {file.name}:", 
            options=df.columns.tolist(), 
            default=df.columns.tolist(), 
            key=f"columns_{key_base}"
        )
        if selected_columns:
            df = df[selected_columns]
            st.dataframe(df.head())
        else:
            st.warning("No columns selected. Displaying all columns by default.")

        # -------- Visualization -------- #
        st.markdown("#### Data Visualization")
        if st.checkbox(f"Show visualization for {file.name}", key=f"visualize_{key_base}"):
            num_cols = df.select_dtypes(include=["number"]).columns
            if len(num_cols) >= 1:
                st.bar_chart(df[num_cols].head())
            else:
                st.info("No numeric columns available for visualization.")

        # -------- Conversion Options -------- #
        st.markdown("#### Conversion Options")
        conversion_type = st.radio(
            f"Convert {file.name} to:", 
            ["CSV", "Excel"], 
            key=f"conversion_{key_base}"
        )
        if st.button(f"Convert {file.name}", key=f"convert_{key_base}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                converted_file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False)
                converted_file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)
            st.download_button(
                label=f"Download converted file: {converted_file_name}",
                data=buffer,
                file_name=converted_file_name,
                mime=mime_type,
                key=f"download_{key_base}"
            )
            st.success("File conversion successful!")
