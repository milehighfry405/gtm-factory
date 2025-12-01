"""
Header Component - Compact header with context meter and research flag.
Claude Desktop style.
"""

import streamlit as st


class Header:
    """
    Compact header bar with title, context meter, and research flag.

    Displays horizontally across the top of the screen.
    """

    def render(self):
        """Render compact header with sticky positioning."""

        # CSS for sticky header
        st.markdown("""
        <style>
        /* Sticky header container */
        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:first-child {
            position: sticky;
            top: 0;
            background-color: #0e1117;
            z-index: 999;
            padding-top: 1rem;
            padding-bottom: 0.5rem;
        }
        </style>
        """, unsafe_allow_html=True)

        # Create horizontal layout (3 columns now, removed research toggle)
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            # Title with mode badge
            title_html = "<h3 style='display: inline;'>GTM Factory</h3>"

            # Add mode badge if mode is selected
            if st.session_state.research_mode:
                mode_display = {
                    "icp-validation": "ICP Validation",
                    "gtm-execution": "GTM Execution",
                    "general": "General Research"
                }
                mode_name = mode_display.get(st.session_state.research_mode, st.session_state.research_mode)
                title_html += f" <span style='font-size: 0.7rem; background-color: #262730; padding: 0.2rem 0.5rem; border-radius: 0.3rem; margin-left: 0.5rem;'>{mode_name}</span>"

            st.markdown(title_html, unsafe_allow_html=True)

        with col2:
            # Context meter (compact)
            if st.session_state.context_tracker is not None:
                tracker = st.session_state.context_tracker
                tracker.add_conversation(st.session_state.messages)

                # Use the format_display() method
                st.caption(f"Context: {tracker.format_display()}")
            else:
                st.caption("Context: --")

        with col3:
            # Placeholder for future controls
            st.write("")

        # Divider below header
        st.divider()
