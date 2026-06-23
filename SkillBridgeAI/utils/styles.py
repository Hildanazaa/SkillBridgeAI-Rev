import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; box-sizing: border-box; }
    .stApp { background: #f8fafc; }
    #MainMenu, footer, header { visibility: hidden; }
    h1, h2, h3, h4, h5, h6 { color: #111827; }
    p, label, span { color: #374151; }
    .stButton > button { background: #1e3a5f; color: #ffffff; border: none; border-radius: 8px; font-weight: 600; font-size: 14px; padding: 10px 24px; width: 100%; cursor: pointer; transition: background 0.2s; }
    .stButton > button:hover { background: #2d4f7c; }
    .stButton > button p { color: #ffffff !important; margin: 0; }
    .stTextArea textarea { background: #ffffff !important; color: #111827 !important; border: 1.5px solid #d1d5db !important; border-radius: 10px !important; font-size: 14px !important; padding: 12px !important; }
    .stTextArea textarea::placeholder { color: #9ca3af !important; }
    .stSelectbox > div > div { background: #ffffff !important; border: 1.5px solid #d1d5db !important; border-radius: 10px !important; color: #111827 !important; }
    .stSelectbox svg { fill: #6b7280 !important; }
    .stTabs [data-baseweb="tab-list"] { background: #f1f5f9; border-radius: 10px; padding: 4px; border: 1px solid #e2e8f0; gap: 4px; display: flex; width: 100%; }
    .stTabs [data-baseweb="tab"] { border-radius: 7px; color: #64748b; font-weight: 700; font-size: 13px; padding: 6px 16px; flex: 1; text-align: center; justify-content: center; }
    .stTabs [aria-selected="true"] { background: #1e3a5f !important; color: #ffffff !important; }
    .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span, .stTabs [aria-selected="true"] { color: #ffffff !important; }
    .stTabs [aria-selected="false"] { color: #374151 !important; }
    [data-testid="stMetric"] { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 16px; }
    [data-testid="stMetricLabel"] p { color: #6b7280 !important; font-size: 12px !important; }
    [data-testid="stMetricValue"] { color: #111827 !important; font-size: 22px !important; font-weight: 700 !important; }
    [data-testid="stVerticalBlockBorderWrapper"] { border: none !important; background: transparent !important; box-shadow: none !important; padding: 0 !important; }
    .stExpander { border: 1px solid #e5e7eb !important; border-radius: 8px !important; background: #ffffff !important; }
    .stExpander summary { color: #111827 !important; font-weight: 500 !important; }
    .stAlert { border-radius: 8px !important; }
    .badge-missing { display: inline-block; background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; border-radius: 6px; padding: 4px 12px; font-size: 12px; font-weight: 600; margin: 3px; }
    .badge-owned { display: inline-block; background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; border-radius: 6px; padding: 4px 12px; font-size: 12px; font-weight: 600; margin: 3px; }
    </style>
    """, unsafe_allow_html=True)
