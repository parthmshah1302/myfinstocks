import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        .big-font {
            font-size: 24px !important;
            font-weight: bold;
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        .positive-return { color: #28a745; }
        .negative-return { color: #dc3545; }
        .section-divider {
            margin: 2rem 0;
            border-bottom: 1px solid #e9ecef;
        }
        .header-container {
            padding: 1rem 0;
            margin-bottom: 2rem;
        }
        .info-text {
            color: #6c757d;
            font-size: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)