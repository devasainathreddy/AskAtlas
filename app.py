"""AskAtlas - Multi-Agent AI Assistant

A Streamlit chat interface for the AskAtlas agent system.
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Inject Streamlit Cloud secrets into os.environ if running in cloud
try:
    if hasattr(st, "secrets"):
        for k, v in st.secrets.items():
            if isinstance(v, str) and k not in os.environ:
                os.environ[k] = v
except Exception:
    pass

from src.graph.workflow import run_query
from src.config import get_settings

# Page configuration
st.set_page_config(
    page_title="AskAtlas",
    page_icon="🌌",
    layout="centered",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# DISTINCTIVE AESTHETIC: EDITORIAL COSMOS
# Fonts: Cormorant Garamond (Classical, Elegant) + DM Sans (Clean, Modern)
# Vibe: A sophisticated, magazine-like interface focusing on typography and depth.
# -----------------------------------------------------------------------------

st.markdown("""
<style>
    /* 1. TYPOGRAPHY & IMPORTS */
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,600;1,600&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&display=swap');
    
    :root {
        --bg-main: #0E1116;
        --bg-secondary: #161B22;
        --accent-primary: #7EE787; /* Neon Mint */
        --accent-secondary: #2F363D;
        --text-primary: #E6EDF3;
        --text-secondary: #8B949E;
        --border-color: #30363D;
        --font-display: 'Cormorant Garamond', serif;
        --font-body: 'DM Sans', sans-serif;
    }

    /* 2. GLOBAL RESET & BASE STYLES */
    .stApp {
        background-color: var(--bg-main);
        background-image: radial-gradient(circle at 50% 0%, #1c2128 0%, #0E1116 100%);
        color: var(--text-primary);
        font-family: var(--font-body);
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-display) !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
        color: var(--text-primary) !important;
    }

    p, div, span, label, button {
        font-family: var(--font-body);
        color: var(--text-primary);
    }

    /* 3. HEADER SECTION */
    .hero-container {
        text-align: center;
        padding: 4rem 0 2rem 0;
        animation: fadeIn 1.2s ease-out;
    }
    
    .hero-title {
        font-family: var(--font-display);
        font-size: 3.5rem;
        font-weight: 300;
        font-style: italic;
        background: linear-gradient(180deg, #FFFFFF 0%, #8B949E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-family: var(--font-body);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--accent-primary);
        opacity: 0.8;
    }

    /* 4. CHAT INTERFACE */
    /* User Message */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: transparent;
        border: 1px solid var(--border-color);
        border-radius: 12px 12px 0 12px; /* Unique shape */
    }
    
    /* Assistant Message */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: var(--bg-secondary);
        border-radius: 12px 12px 12px 0;
        border: none;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }

    /* Avatars */
    .stChatMessage .stChatMessageAvatar {
        background: var(--accent-primary) !important;
        color: var(--bg-main) !important;
        font-weight: bold;
    }

    /* Input Field */
    .stTextInput input {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    /* --- CHAT INPUT FIX --- */

    /* 1. Reset all default Streamlit focus rings and borders */
    .stChatInput {
        padding-bottom: 3.5rem !important; /* Lift input to make room for footer */
    }
    
    .stChatInput * {
        box-shadow: none !important;
        outline: none !important;
    }

    /* 2. Style the Input Wrapper Container */
    [data-testid="stChatInput"] > div {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 24px !important;
        color: var(--text-primary) !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }

    /* 3. Custom Focus State */
    [data-testid="stChatInput"] > div:focus-within {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 15px rgba(126, 231, 135, 0.15) !important;
    }

    /* 4. Textarea Cleanup */
    [data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        border: none !important;
        color: var(--text-primary) !important;
        caret-color: var(--accent-primary) !important;
        padding: 0.8rem 1rem !important;
        min-height: 2.5rem !important;
    }

    /* 5. Send Button Styling */
    [data-testid="stChatInput"] button {
        color: var(--text-secondary) !important;
        border: none !important;
        background: transparent !important;
    }
    
    [data-testid="stChatInput"] button:hover {
        color: var(--accent-primary) !important;
    }

    /* 5. SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] h1 {
        font-size: 1.5rem;
    }
    
    /* 6. UTILITIES & ANIMATIONS */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stButton button {
        background-color: transparent !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-secondary) !important;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        border-color: var(--accent-primary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Custom Badge Logic handled via inline HTML usually, but global class here */
    .visual-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        background: rgba(126, 231, 135, 0.1);
        border: 1px solid rgba(126, 231, 135, 0.2);
        border-radius: 100px;
        font-size: 0.75rem;
        color: var(--accent-primary);
        font-family: var(--font-body);
        margin-bottom: 2rem;
    }

    /* Hide standard Streamlit main menu and footer, but keep Header visible for Sidebar toggle */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    header {
        visibility: visible !important;
        background-color: transparent !important;
    }
    
    /* Optional: Hide the thin colored decoration line at the top if desired, 
       but standard header visibility is prioritized for navigation. */

    /* 7. ALERTS & NOTIFICATIONS */
    .stAlert {
        background-color: rgba(22, 27, 34, 0.8) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
    }
    
    /* Success Icon Color */
    .stAlert [data-testid="stMarkdownContainer"] {
        color: var(--text-primary) !important;
    }

    /* 8. FOOTER */
    .custom-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        text-align: center;
        padding: 1rem 0;
        z-index: 1000;
        pointer-events: none; /* Let clicks pass through */
        background: linear-gradient(to top, var(--bg-main) 0%, transparent 100%);
        transition: left 0.3s ease, width 0.3s ease; /* Smooth transition when toggling */
    }
    .custom-footer a {
        pointer-events: auto;
    }
    
    /* Conditional Offset: Only shift if Sidebar is OPEN on Desktop */
    @media (min-width: 992px) {
        /* Check if the sidebar section exists and is expanded */
        body:has(section[data-testid="stSidebar"][aria-expanded="true"]) .custom-footer {
            left: 21rem;
            width: calc(100% - 21rem);
        }
    }
</style>
""", unsafe_allow_html=True)

# Custom Header Display
st.markdown("""
<div class="hero-container">
    <div class="visual-badge">AskAtlas v1.0</div>
    <div class="hero-title">AskAtlas</div>
    <div class="hero-subtitle">Your Neural Companion</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Custom Status Component
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.05); padding: 0.75rem; border-radius: 8px; border: 1px solid var(--border-color); margin-bottom: 0.5rem;">
            <span style="font-size: 0.8rem; color: var(--text-secondary);">Status</span>
            <span style="font-size: 0.8rem; color: var(--accent-primary); font-weight: 600;">● System Online</span>
        </div>
    """, unsafe_allow_html=True)

    try:
        settings = get_settings()
        # Visual styling for provider info
        provider_icon = {
            "openai": "🤖",
            "google": "🌌",
            "ollama": "🦙",
        }[settings.llm_provider]
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.05); padding: 0.75rem; border-radius: 8px; border: 1px solid var(--border-color);">
                <span style="font-size: 0.8rem; color: var(--text-secondary);">Provider</span>
                <span style="font-size: 0.8rem; color: var(--text-primary);">{provider_icon} {settings.llm_provider.upper()}</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.05); padding: 0.75rem; border-radius: 8px; border: 1px solid var(--border-color);">
                <span style="font-size: 0.8rem; color: var(--text-secondary);">Model</span>
                <span style="font-size: 0.8rem; color: var(--text-primary); font-family: monospace;">{settings.llm_model}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error("Missing API Configuration")
        st.code("OPENAI_API_KEY=...\nOPENWEATHERMAP_API_KEY=...", language="bash")
    
    st.divider()

    st.header("⚡ System Modules")
    st.markdown("""
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.05); padding: 0.5rem 0.75rem; border-radius: 8px; border: 1px solid var(--border-color);">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: #64b5f6;">🔀</span>
                    <span style="font-size: 0.8rem; color: var(--text-primary);">Router</span>
                </div>
                <span style="font-size: 0.7rem; color: var(--accent-primary); opacity: 0.8;">ACTIVE</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.05); padding: 0.5rem 0.75rem; border-radius: 8px; border: 1px solid var(--border-color);">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: #ffb74d;">🌤️</span>
                    <span style="font-size: 0.8rem; color: var(--text-primary);">Weather Agent</span>
                </div>
                <span style="font-size: 0.7rem; color: var(--accent-primary); opacity: 0.8;">READY</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.05); padding: 0.5rem 0.75rem; border-radius: 8px; border: 1px solid var(--border-color);">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: #81c784;">📚</span>
                    <span style="font-size: 0.8rem; color: var(--text-primary);">RAG Agent</span>
                </div>
                <span style="font-size: 0.7rem; color: var(--accent-primary); opacity: 0.8;">LINKED</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    
    st.header("✦ Suggestions")
    
    # Styled Suggestion Cards
    suggestion_style = """
    <div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border: 1px solid var(--border-color); transition: all 0.2s; cursor: pointer;">
        <div style="font-size: 0.7rem; text-transform: uppercase; color: var(--accent-primary); margin-bottom: 0.25rem;">{category}</div>
        <div style="font-size: 0.9rem; color: var(--text-primary);">"{text}"</div>
    </div>
    """
    
    st.markdown(suggestion_style.format(category="General", text="Hello! How are you?"), unsafe_allow_html=True)
    st.markdown(suggestion_style.format(category="Weather", text="Temperature in Mumbai?"), unsafe_allow_html=True)
    st.markdown(suggestion_style.format(category="RAG", text="Explain embeddings"), unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Empty State / Landing Visual
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; height: 300px; opacity: 0.5;">
        <div style="
            width: 150px; 
            height: 150px; 
            border-radius: 50%; 
            background: radial-gradient(circle, var(--accent-primary) 0%, transparent 70%); 
            filter: blur(40px);
            animation: pulse-glow 4s infinite ease-in-out;
            ">
        </div>
    </div>
    <style>
    @keyframes pulse-glow {
        0% { transform: scale(0.8); opacity: 0.3; }
        50% { transform: scale(1.1); opacity: 0.6; }
        100% { transform: scale(0.8); opacity: 0.3; }
    }
    </style>
    """, unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about weather or documents..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = run_query(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer (Fixed)
st.markdown(
    """
    <div class="custom-footer">
    <span style='letter-spacing: 1px; color: var(--text-secondary); font-size: 0.7rem;'>DESIGNED WITH INTELLIGENCE</span>
    <span style='margin: 0 0.5rem; color: var(--border-color);'>|</span>
    <a href='https://smith.langchain.com' target='_blank' style='color: var(--accent-primary); font-size: 0.7rem; text-decoration: none;'>View Trace</a>
    </div>
    """,
    unsafe_allow_html=True
)
