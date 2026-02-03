import streamlit as st
import pandas as pd
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI
import os
import time
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import plotly.express as px

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide"
)

# --- Header ---
st.title("📊 AI Data Analyst Agent")
st.markdown("""
Upload a CSV file and ask questions about your data!
*Powered by OpenAI and PandasAI (Legacy Mode)*
""")

# --- Sidebar ---
with st.sidebar:
    st.header("Configuration")
    
    # Try to get key from env, otherwise ask user
    env_key = os.getenv("OPENAI_API_KEY")
    api_key = st.text_input("OpenAI API Key", value=env_key if env_key else "", type="password")
    
    if not api_key:
        st.warning("⚠️ Please provide an API Key to proceed.")
        
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

# --- Main Logic ---
import random

# --- Mock AI Class for Demo Mode ---
class MockPandasAI:
    def run(self, df, prompt=""):
        time.sleep(1) # Simulate thinking
        prompt = prompt.lower()
        if "plot" in prompt or "chart" in prompt or "trend" in prompt:
            # Generate a random plot (using matplotlib directly for demo)
            plt.figure(figsize=(10, 5))
            # Try to plot numeric columns
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) > 0:
                col = numeric_cols[0]
                plt.bar(df.head(10).index, df.head(10)[col])
                plt.title(f"Demo Chart: {col} (Mock Intepretation)")
                plt.xlabel("Index")
                plt.ylabel(col)
            else:
                plt.text(0.5, 0.5, "No numeric data to plot", ha='center')
            return "Here is a visualization based on your request (Demo Mode)."
        elif "recommendation" in prompt or "insight" in prompt:
            return """
            **Mock Insights (Demo Mode):**
            1.  **Trend Observed:** Sales show a positive correlation with time.
            2.  **Action Item:** Invest in region 'North' as it shows high potential.
            3.  **Data Quality:** The dataset appears clean with no missing values.
            """
        else:
            return f"I processed your request: '{prompt}'. \n\n(This is a demo response. Add a valid API Key to get real AI analysis.)"

import plotly.express as px

# --- Main Logic ---
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("### Data Preview")
        st.dataframe(df.head())
        
        # Determine Mode
        ai_enabled = bool(api_key)
        
        # Tabs for different features
        tab1, tab2 = st.tabs(["📈 Manual Visualization", "🤖 AI Analyst"])
        
        # --- TAB 1: Manual Visualization (Works without API Key) ---
        with tab1:
            st.subheader("Build you own charts")
            st.info("Select columns to visualize them manually.")
            
            # Column selection
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            all_cols = df.columns.tolist()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Scatter", "Histogram", "Box"])
            with col2:
                x_col = st.selectbox("X Axis", all_cols)
            with col3:
                if chart_type in ["Histogram", "Box"]:
                    y_col = None
                else:
                    y_col = st.selectbox("Y Axis", numeric_cols if numeric_cols else all_cols)
            
            if st.button("Generate Chart"):
                if chart_type == "Bar":
                    fig = px.bar(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
                elif chart_type == "Line":
                    fig = px.line(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
                elif chart_type == "Scatter":
                    fig = px.scatter(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
                elif chart_type == "Histogram":
                    fig = px.histogram(df, x=x_col, title=f"Distribution of {x_col}")
                elif chart_type == "Box":
                    fig = px.box(df, x=x_col, title=f"Box Plot of {x_col}")
                
                st.plotly_chart(fig, use_container_width=True)

        # --- TAB 2: AI Analyst (Requires API Key or runs in Mock Mode) ---
        with tab2:
            st.subheader("Ask the AI")
            
            if not ai_enabled:
                 st.warning("⚠️ No Valid API Key detected. Using **Demo Mode** (Mock Responses).")
                 agent = MockPandasAI()
                 mode_label = "Demo Mode"
            else:
                 st.success("✅ AI Online. Using OpenAI.")
                 llm = OpenAI(api_token=api_key)
                 agent = PandasAI(llm, enable_cache=False)
                 mode_label = "Real AI"

            query = st.text_area("What would you like to know?", placeholder="e.g., Plot sales by region")
            
            if st.button("Generate Answer"):
                if query:
                    with st.spinner(f"Thinking ({mode_label})..."):
                        try:
                            response = agent.run(df, prompt=query)
                            st.write(response)
                            if plt.get_fignums():
                                st.pyplot(plt.gcf())
                                plt.clf()
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            st.markdown("---")
            if st.button("Get Business Insights"):
                 with st.spinner(f"Analyzing ({mode_label})..."):
                    try:
                        if ai_enabled:
                             prompt = "Analyze this dataset and provide 3 key insights and recommendations."
                             response = agent.run(df, prompt=prompt)
                        else:
                            response = agent.run(df, prompt="insight")
                        st.write(response)
                    except Exception as e:
                        st.error(f"Error: {e}")

    except Exception as e:
        st.error(f"Error reading file: {e}")

elif uploaded_file is None:
    st.info("👆 Please upload a CSV file to begin.")
    
    if st.button("Use Sample Data"):
        # Create a sample CSV for the user to download/use
        data = {
            'Date': pd.date_range(start='1/1/2023', periods=10),
            'Product': ['Widget A', 'Widget B', 'Widget C', 'Widget A', 'Widget B', 'Widget C', 'Widget A', 'Widget B', 'Widget C', 'Widget A'],
            'Sales': [100, 150, 80, 120, 160, 90, 110, 140, 85, 130],
            'Region': ['North', 'North', 'South', 'South', 'East', 'East', 'West', 'West', 'North', 'South']
        }
        df_sample = pd.DataFrame(data)
        df_sample.to_csv("sample_sales.csv", index=False)
        st.success("Created 'sample_sales.csv'! Drag and drop it into the uploader.")
        st.dataframe(df_sample)

