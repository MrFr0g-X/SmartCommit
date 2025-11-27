"""
SmartCommit Streamlit UI
iOS 26 Liquid Glass Design
"""

import streamlit as st
import requests
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="SmartCommit",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for iOS Liquid Glass design
st.markdown("""
<style>
    /* Import SF Pro font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
    }

    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }

    /* Card styling with glassmorphism */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }

    /* Text colors */
    h1, h2, h3, p, label, .stMarkdown {
        color: white !important;
    }

    /* Button styling */
    .stButton > button {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.5);
        transform: translateY(-2px);
    }

    /* Textarea styling */
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        color: white;
        font-family: 'Monaco', 'Courier New', monospace;
    }

    /* Success/Error messages */
    .stSuccess {
        background: rgba(76, 175, 80, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 1px solid rgba(76, 175, 80, 0.3);
    }

    .stError {
        background: rgba(244, 67, 54, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 1px solid rgba(244, 67, 54, 0.3);
    }

    /* Metrics */
    .stMetric {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_URL = "http://localhost:8000"


def call_generate_api(diff: str) -> dict:
    """Call the /generateCommit endpoint"""
    try:
        response = requests.post(
            f"{API_URL}/generateCommit",
            json={"diff": diff},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure the backend is running on port 8000")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def call_check_api(diff: str, message: str, reference: str = None) -> dict:
    """Call the /checkCommit endpoint"""
    try:
        payload = {
            "diff": diff,
            "commit_message": message
        }
        if reference:
            payload["reference_message"] = reference

        response = requests.post(
            f"{API_URL}/checkCommit",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure the backend is running on port 8000")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


# App title
st.markdown("# 🤖 SmartCommit")
st.markdown("### AI-Powered Commit Message Generator")

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    mode = st.radio(
        "Select Mode",
        ["Generate", "Check Quality"],
        help="Generate new messages or check existing ones"
    )

    st.markdown("---")
    st.markdown("### 📊 About")
    st.markdown("SmartCommit uses Google Gemini 2.0 Flash to generate and evaluate commit messages.")
    st.markdown("Built for SW403 - Phase 2")

# Main content
if mode == "Generate":
    st.markdown("## 📝 Generate Commit Message")

    # Input area
    diff_input = st.text_area(
        "Paste your git diff here:",
        height=300,
        placeholder="diff --git a/file.py b/file.py\n...",
        help="Paste the output of 'git diff' command"
    )

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        generate_btn = st.button("🚀 Generate", use_container_width=True)

    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    if generate_btn:
        if not diff_input.strip():
            st.warning("⚠️ Please paste a diff first")
        else:
            with st.spinner("Generating commit message..."):
                result = call_generate_api(diff_input)

                if result:
                    st.success("✅ Message generated successfully!")

                    # Display result
                    st.markdown("### Generated Message:")
                    st.code(result['message'], language=None)

                    # Metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Model", result['model'])
                    with col2:
                        st.metric("Latency", f"{result['latency_ms']}ms")
                    with col3:
                        st.metric("Time", datetime.fromisoformat(result['timestamp']).strftime("%H:%M:%S"))

                    # Save to session state
                    st.session_state['last_message'] = result['message']
                    st.session_state['last_diff'] = diff_input

else:  # Check Quality mode
    st.markdown("## 🔍 Check Commit Quality")

    # Load from previous generation if available
    default_diff = st.session_state.get('last_diff', '')
    default_msg = st.session_state.get('last_message', '')

    diff_input = st.text_area(
        "Git Diff:",
        value=default_diff,
        height=200,
        placeholder="diff --git a/file.py b/file.py\n..."
    )

    commit_msg = st.text_area(
        "Commit Message to Check:",
        value=default_msg,
        height=100,
        placeholder="Add feature X to improve performance"
    )

    reference_msg = st.text_area(
        "Reference Message (optional):",
        height=100,
        placeholder="Leave empty to skip BLEU/ROUGE comparison",
        help="Provide a human-written message for comparison"
    )

    if st.button("🔍 Check Quality", use_container_width=True):
        if not diff_input.strip() or not commit_msg.strip():
            st.warning("⚠️ Please provide both diff and message")
        else:
            with st.spinner("Analyzing quality..."):
                result = call_check_api(
                    diff_input,
                    commit_msg,
                    reference_msg if reference_msg.strip() else None
                )

                if result:
                    st.success("✅ Analysis complete!")

                    # Metrics in columns
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("BLEU-4", f"{result['bleu']:.2f}")

                    with col2:
                        st.metric("ROUGE-L", f"{result['rouge']['rougeL']:.2f}")

                    with col3:
                        st.metric("Semantic Sim", f"{result['semantic_similarity']:.3f}")

                    with col4:
                        quality_score = result['quality_score']
                        st.metric(
                            "Quality Score",
                            f"{quality_score:.2f}",
                            delta="Good" if quality_score > 0.7 else "Poor"
                        )

                    # Hallucination detection
                    st.markdown("### 🔬 Hallucination Analysis")

                    hall = result['hallucination']
                    if hall['detected']:
                        st.error(f"⚠️ Potential hallucination detected ({hall['hallucination_rate']*100:.1f}%)")
                        if hall['ungrounded_tokens']:
                            st.markdown(f"**Ungrounded tokens:** {', '.join(hall['ungrounded_tokens'][:10])}")
                    else:
                        st.success("✅ No hallucinations detected")

                    # Feedback
                    st.markdown("### 💡 Feedback")
                    for feedback in result['feedback']:
                        st.markdown(f"- {feedback}")

# Footer
st.markdown("---")
st.markdown(
    "<center>Built with Streamlit | SmartCommit v0.1.0 | SW403 Phase 2</center>",
    unsafe_allow_html=True
)
