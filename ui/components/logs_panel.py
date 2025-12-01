"""
Logs Panel Component - In-app debugging and error logs.
"""

import streamlit as st
from datetime import datetime


class LogsPanel:
    """
    Display logs for debugging.

    Shows:
    - Info messages
    - Warnings
    - Errors
    """

    def render(self):
        """Render logs panel."""

        with st.expander("🪵 Logs", expanded=False):
            # Initialize logs if not exists
            if "logs" not in st.session_state:
                st.session_state.logs = []

            # Display logs
            if st.session_state.logs:
                for log in st.session_state.logs[-50:]:  # Last 50 logs
                    timestamp = log.get("timestamp", "")
                    level = log.get("level", "INFO")
                    message = log.get("message", "")

                    if level == "ERROR":
                        st.error(f"[{timestamp}] {message}")
                    elif level == "WARNING":
                        st.warning(f"[{timestamp}] {message}")
                    else:
                        st.info(f"[{timestamp}] {message}")

                if st.button("Clear Logs"):
                    st.session_state.logs = []
                    st.rerun()
            else:
                st.info("No logs yet")

    @staticmethod
    def log(message: str, level: str = "INFO"):
        """
        Add log message.

        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR)
        """
        if "logs" not in st.session_state:
            st.session_state.logs = []

        st.session_state.logs.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": message
        })
