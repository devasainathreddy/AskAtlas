"""AskAtlas - Multi-Agent AI Assistant

A Streamlit chat interface for the AskAtlas agent system.
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Inject Streamlit Cloud / local secrets into os.environ
try:
    if hasattr(st, "secrets"):
        for k in [
            "GROQ_API_KEY",
            "GOOGLE_API_KEY",
            "OPENAI_API_KEY",
            "OPENWEATHERMAP_API_KEY",
            "LLM_PROVIDER",
            "LLM_MODEL",
            "QDRANT_URL",
            "QDRANT_API_KEY",
        ]:
            if k in st.secrets and k not in os.environ:
                os.environ[k] = str(st.secrets[k])
        for k, v in st.secrets.items():
            if isinstance(v, str) and k not in os.environ:
                os.environ[k] = v
except Exception:
    pass

from src.graph.workflow import run_query
from src.config import get_settings


def format_api_error(e: Exception) -> str:
    """Format exceptions into user-friendly messages for quota, auth, and network errors."""
    try:
        import groq

        if isinstance(e, groq.AuthenticationError):
            return (
                "🔑 **Authentication Error:** Invalid or missing Groq API Key. "
                "Please verify `GROQ_API_KEY` in Streamlit secrets or your `.env` file."
            )
        elif isinstance(e, groq.RateLimitError):
            return (
                "⏳ **Quota / Rate Limit Exceeded:** You have reached Groq's free-tier rate limit (TPM/RPM). "
                "Please wait a few seconds and try again."
            )
        elif isinstance(e, groq.APITimeoutError):
            return "⏱️ **Timeout Error:** The Groq API request timed out. Please try again."
        elif isinstance(e, groq.APIConnectionError):
            return (
                "🌐 **Network Error:** Could not connect to the Groq API servers. "
                "Please check your internet connection."
            )
        elif isinstance(e, groq.GroqError):
            return f"⚠️ **Groq API Error:** {str(e)}"
    except ImportError:
        pass

    err_str = str(e).lower()
    if "401" in err_str or "invalid api key" in err_str or "unauthorized" in err_str or "authentication" in err_str:
        return (
            "🔑 **Authentication Error:** Invalid Groq API Key. "
            "Please check `GROQ_API_KEY` in Streamlit secrets or your `.env` file."
        )
    if "429" in err_str or "rate limit" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
        return (
            "⏳ **Quota / Rate Limit Exceeded:** Groq free-tier rate limit reached. "
            "Please wait a moment and try again."
        )
    if "connection" in err_str or "failed to connect" in err_str or "network" in err_str:
        return "🌐 **Network Error:** Failed to establish connection to Groq API. Please check your network."

    return f"❌ **Error:** {str(e)}"


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
            "groq": "⚡",
            "openai": "🤖",
            "google": "🌌",
            "ollama": "🦙",
        }.get(settings.llm_provider, "⚡")
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
        st.code("GROQ_API_KEY=gsk_...", language="bash")

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
    
    if st.button("💬 'Hello! How are you?'", use_container_width=True, disabled=st.session_state.get("is_processing", False)):
        st.session_state.pending_prompt = "Hello! How are you?"
        st.rerun()
    if st.button("⛅ 'Temperature in Mumbai?'", use_container_width=True, disabled=st.session_state.get("is_processing", False)):
        st.session_state.pending_prompt = "Temperature in Mumbai?"
        st.rerun()
    if st.button("📚 'Explain embeddings'", use_container_width=True, disabled=st.session_state.get("is_processing", False)):
        st.session_state.pending_prompt = "Explain embeddings"
        st.rerun()
    
    st.divider()

    # API Key check banner
    settings = get_settings()
    has_api_key = bool(
        (settings.groq_api_key or "").strip()
        or (settings.google_api_key or "").strip()
        or (settings.openai_api_key or "").strip()
    )
    if not has_api_key:
        st.warning("⚠️ No Groq API key found. Add `GROQ_API_KEY` to your Streamlit Secrets or `.env`.")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.is_processing = False
        st.session_state.pending_prompt = None
        st.rerun()

# Initialize chat history and state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

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

# Collect user prompt (preventing duplicate calls during reruns)
new_prompt = None
if st.session_state.pending_prompt:
    new_prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
elif user_input := st.chat_input("Ask about weather or documents...", disabled=st.session_state.is_processing):
    new_prompt = user_input

# Execute query safely without duplicate invocations
if new_prompt and not st.session_state.is_processing:
    st.session_state.is_processing = True
    st.session_state.messages.append({"role": "user", "content": new_prompt})
    with st.chat_message("user"):
        st.markdown(new_prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking with Groq..."):
            try:
                response = run_query(new_prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = format_api_error(e)
                st.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            finally:
                st.session_state.is_processing = False

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
