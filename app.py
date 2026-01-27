import json
import streamlit as st
import polars as pl

from ingestion.load_csv import load_csv
from profiling.stats import descriptive_statistics
from profiling.missing_values import missing_value_analysis
from profiling.markdown_writer import generate_markdown_report


# -------------------- Streamlit Config --------------------
st.set_page_config(
    page_title="RAG-based CSV Analyzer",
    layout="wide"
)

st.title("📊 RAG-based CSV Analyzer")
st.write("Upload a CSV file to generate profiling reports.")


# -------------------- File Uploader --------------------
uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"]
)


if uploaded_file is not None:
    # -------------------- Load CSV --------------------
    try:
        # Polars can read file-like objects directly
        df = pl.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        st.stop()

    # -------------------- Dataset Info --------------------
    dataset_info = {
        "rows": df.height,
        "columns": df.width,
        "schema": {
            col: str(dtype)
            for col, dtype in zip(df.columns, df.dtypes)
        }
    }

    st.subheader("📌 Dataset Overview")
    col1, col2 = st.columns(2)
    col1.metric("Rows", dataset_info["rows"])
    col2.metric("Columns", dataset_info["columns"])

    st.subheader("🧬 Schema")
    st.json(dataset_info["schema"])

    # -------------------- Profiling --------------------
    with st.spinner("Running data profiling..."):
        stats = descriptive_statistics(df)
        missing_values = missing_value_analysis(df)

    # -------------------- Results --------------------
    st.subheader("📈 Descriptive Statistics")
    st.json(stats)

    st.subheader("❌ Missing Value Analysis")
    st.json(missing_values)

    # -------------------- Markdown Report --------------------
    md_report = generate_markdown_report(
        dataset_info,
        stats,
        missing_values
    )

    st.subheader("📝 Auto-generated Markdown Report")
    st.markdown(md_report)

    # -------------------- Downloads --------------------
    report_json = {
        "dataset_info": dataset_info,
        "descriptive_statistics": stats,
        "missing_value_analysis": missing_values
    }

    st.download_button(
        label="⬇️ Download JSON Report",
        data=json.dumps(report_json, indent=4),
        file_name="profiling_report.json",
        mime="application/json"
    )

    st.download_button(
        label="⬇️ Download Markdown Report",
        data=md_report,
        file_name="profiling_report.md",
        mime="text/markdown"
    )