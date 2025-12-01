"""
GTM Factory - Main Streamlit Application

Entry point for the GTM Factory research system.
Integrates HQ chat, research execution, and drop management.

Run with: streamlit run ui/app.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
import logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(message)s',
    force=True
)
logging.getLogger("gpt_researcher").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logging.getLogger("tavily").setLevel(logging.ERROR)

import streamlit as st

# Import UI components
from ui.components.header import Header
from ui.components.chat_interface import ChatInterface
from ui.components.progress_display import ProgressDisplay
from ui.utils.session_loader import SessionLoader
from ui.utils.crash_recovery import CrashRecovery

# Import adapters
from core.ui import StateManager, ContextTracker, HQAdapter, ResearcherAdapter, GeneratorAdapter, DropState
from anthropic import Anthropic
import re
from datetime import datetime

# Page config - Claude Desktop style (full screen, no sidebar)
st.set_page_config(
    page_title="GTM Factory",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.messages = []
    st.session_state.research_flag = False
    st.session_state.current_drop_id = None
    st.session_state.drop_counter = 0
    st.session_state.cancel_research = False  # Kill switch flag

    # Session will be generated from first message
    st.session_state.session_id = None  # Generated after first message
    st.session_state.session_name_generated = False

    # Research mode (selected before first message)
    st.session_state.research_mode = None  # Set by mode selector

    # Adapters (will be initialized after session name generated)
    st.session_state.hq_adapter = None
    st.session_state.researcher_adapter = None
    st.session_state.generator_adapter = None
    st.session_state.state_manager = None
    st.session_state.context_tracker = None

def generate_session_name(first_message: str) -> str:
    """Generate session name from first user message (like Helldiver)."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    client = Anthropic(api_key=api_key)

    prompt = f"""Generate a concise session name from this GTM hypothesis:

"{first_message}"

Return ONLY a short, descriptive name (2-4 words, lowercase, hyphenated).
Examples: "b2b-saas-outbound", "smb-product-led-growth", "enterprise-cold-email"

Session name:"""

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=50,
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract and clean the session name
    session_name = response.content[0].text.strip().lower()
    # Remove quotes if present
    session_name = session_name.strip('"').strip("'")
    # Sanitize: only lowercase, hyphens, numbers
    session_name = re.sub(r'[^a-z0-9-]', '-', session_name)
    session_name = re.sub(r'-+', '-', session_name).strip('-')

    # Add timestamp to make it unique
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{session_name}-{timestamp}"

def initialize_adapters():
    """Initialize all adapters with API keys and mode."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("ANTHROPIC_API_KEY not found in environment variables")
        st.stop()

    # Ensure mode is selected
    if not st.session_state.research_mode:
        st.error("Research mode not selected. Please refresh and select a mode.")
        st.stop()

    project_path = Path("projects")
    session_path = project_path / "sessions" / st.session_state.session_id

    # Initialize adapters with mode
    st.session_state.hq_adapter = HQAdapter(
        api_key=api_key,
        project_path=project_path,
        session_id=st.session_state.session_id,
        mode=st.session_state.research_mode
    )
    st.session_state.researcher_adapter = ResearcherAdapter()
    st.session_state.generator_adapter = GeneratorAdapter()
    st.session_state.state_manager = StateManager(session_path=session_path)
    st.session_state.context_tracker = ContextTracker()

def check_crash_recovery():
    """Check for incomplete drops and offer recovery."""
    recovery = CrashRecovery(state_manager=st.session_state.state_manager)
    incomplete_drops = recovery.find_incomplete_drops()

    if incomplete_drops:
        st.sidebar.warning(f"Found {len(incomplete_drops)} incomplete drop(s)")

        for drop in incomplete_drops:
            drop_id = drop["drop_id"]
            state = drop["state"]

            with st.sidebar.expander(f"⚠️ {drop_id} ({state})"):
                st.write(f"Created: {drop.get('created_at', 'Unknown')}")
                st.write(f"State: {state}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Mark {drop_id} as failed", key=f"fail_{drop_id}"):
                        st.session_state.state_manager.update_drop_state(drop_id, DropState.FAILED)
                        st.rerun()

                with col2:
                    if st.button(f"Resume {drop_id}", key=f"resume_{drop_id}"):
                        # TODO: Implement resume logic
                        st.info("Resume not yet implemented. Mark as failed for now.")

def main():
    """Main application loop."""

    # Only initialize adapters if session name has been generated
    # (Otherwise wait for first message to generate session name)
    if st.session_state.session_name_generated and st.session_state.hq_adapter is None:
        initialize_adapters()

    # Check for crash recovery (only if adapters initialized)
    if st.session_state.hq_adapter is not None:
        check_crash_recovery()

        # Load saved conversation if exists
        if not st.session_state.messages:
            saved_messages = st.session_state.state_manager.load_conversation()
            if saved_messages:
                st.session_state.messages = saved_messages
                st.session_state.hq_adapter.load_conversation_history(saved_messages)

        # Load saved session state (mode, research flag, etc.)
        if st.session_state.research_mode:
            # Save mode to session state file (persists across crashes)
            st.session_state.state_manager.save_session_state({
                "research_mode": st.session_state.research_mode,
                "research_flag": st.session_state.research_flag,
                "drop_counter": st.session_state.drop_counter
            })
        else:
            # Try to load mode from saved state
            saved_state = st.session_state.state_manager.load_session_state()
            if saved_state and "research_mode" in saved_state:
                st.session_state.research_mode = saved_state["research_mode"]
                st.session_state.research_flag = saved_state.get("research_flag", False)
                st.session_state.drop_counter = saved_state.get("drop_counter", 0)

    # Compact header (title, context meter, research flag)
    header = Header()
    header.render()

    # Main chat interface (full width, Claude Desktop style)
    chat_interface = ChatInterface()
    chat_interface.render()

    # Progress display (only shows when research active)
    progress_display = ProgressDisplay()
    progress_display.render()

if __name__ == "__main__":
    main()
