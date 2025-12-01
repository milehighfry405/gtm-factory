"""
Chat Interface Component - Claude Desktop style conversation UI.
"""

import streamlit as st
import asyncio
from pathlib import Path
import time


class ChatInterface:
    """
    Chat interface for HQ conversations (Claude Desktop style).

    Features:
    - Full viewport height
    - Left-aligned messages
    - Immediate message display (user message shows instantly)
    - Streaming responses with thinking indicator
    - Research plan confirmation
    """

    def render(self):
        """Render chat interface."""

        # Custom CSS for Claude Desktop-style layout
        st.markdown("""
        <style>
        /* Full viewport utilization */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            max-width: 100%;
        }

        /* Chat messages left-aligned, max-width for readability */
        [data-testid="stChatMessageContent"] {
            max-width: 800px;
        }

        /* Input area styling */
        [data-testid="stChatInput"] {
            max-width: 900px;
            margin: 0 auto;
        }

        /* Remove extra padding */
        .stChatFloatingInputContainer {
            padding-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

        # Mode selector (only show if no messages, session not initialized, AND mode not selected)
        if not st.session_state.messages and not st.session_state.session_name_generated and not st.session_state.research_mode:
            self._show_mode_selector()
            return  # Don't show chat input until mode is selected

        # Display conversation history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Show thinking indicator if streaming
        if st.session_state.get("is_thinking", False):
            with st.chat_message("assistant"):
                st.markdown("...")

        # Research toggle above chat input (cleaner layout)
        col1, col2, col3 = st.columns([1, 6, 1])

        with col1:
            st.write("")  # Spacing

        with col2:
            # Research mode toggle with icon
            research_flag = st.toggle(
                "🔬 Research Mode",
                value=st.session_state.research_flag,
                key="research_toggle",
                help="Enable to trigger research on next message"
            )
            # Update session state (Streamlit will rerun automatically on toggle change)
            if research_flag != st.session_state.research_flag:
                st.session_state.research_flag = research_flag

        with col3:
            st.write("")  # Spacing

        # User input (naturally sticky at bottom by Streamlit)
        prompt = st.chat_input("Message GTM Factory...")

        if prompt:
            # Generate session name from first message if not done yet
            if not st.session_state.session_name_generated:
                # Import here to avoid circular dependency
                from ui.app import generate_session_name, initialize_adapters

                with st.spinner("Creating new session..."):
                    # Generate session name
                    session_name = generate_session_name(prompt)
                    st.session_state.session_id = session_name
                    st.session_state.session_name_generated = True

                    # Now initialize adapters with the new session name
                    initialize_adapters()

            # Add user message IMMEDIATELY (Claude Desktop behavior)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Display user message immediately with placeholder for assistant
            with st.chat_message("user"):
                st.markdown(prompt)

            # Show thinking indicator
            message_placeholder = st.empty()
            with message_placeholder.container():
                with st.chat_message("assistant"):
                    thinking_placeholder = st.empty()
                    thinking_placeholder.markdown("...")

            # If research flag is ON, trigger research immediately
            if st.session_state.research_flag:
                # Show HQ's quick acknowledgment
                with st.chat_message("assistant"):
                    st.markdown("Understood. Kicking off research now...")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Understood. Kicking off research now..."
                })

                # Turn OFF research flag (user submitted their research query)
                st.session_state.research_flag = False

                # Trigger research execution
                try:
                    self._trigger_research_execution()
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to start research: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                return

            # Normal chat mode (research flag OFF)
            full_response = ""
            for token in st.session_state.hq_adapter.chat_stream(prompt):
                full_response += token
                # Update display with accumulated response
                with message_placeholder.container():
                    with st.chat_message("assistant"):
                        st.markdown(full_response + "▌")  # Cursor effect

            # Final update (remove cursor)
            with message_placeholder.container():
                with st.chat_message("assistant"):
                    st.markdown(full_response)

            # Add assistant message to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # Autosave conversation
            st.session_state.state_manager.autosave_conversation(st.session_state.messages)

            # Update context tracker
            st.session_state.context_tracker.add_conversation(st.session_state.messages)

            # Streamlit will naturally rerun on next chat_input - no manual rerun needed

    def _trigger_research_execution(self):
        """Trigger research execution after HQ proposes plan."""
        from pathlib import Path

        print("\n" + "="*80)
        print("RESEARCH TRIGGER: Starting research execution")
        print("="*80)

        # Get research plan from HQ
        print("Step 1: Extracting research plan from HQ...")
        plan = st.session_state.hq_adapter.propose_research_plan()
        print(f"Plan received: {plan}")

        if plan is None:
            print("ERROR: HQ returned None for research plan!")
            raise ValueError("HQ failed to generate research plan - returned None")

        # Generate drop ID
        st.session_state.drop_counter += 1
        drop_id = f"drop-{st.session_state.drop_counter}"

        # Create drop folder
        session_path = Path(f"projects/sessions/{st.session_state.session_id}")
        drop_path = session_path / "drops" / drop_id
        drop_path.mkdir(parents=True, exist_ok=True)

        # Extract and save user context
        user_context = st.session_state.hq_adapter.extract_user_context()
        (drop_path / "user-context.md").write_text(user_context, encoding="utf-8")

        # Save conversation history
        conversation_md = "\n\n".join([
            f"**{msg['role'].title()}**: {msg['content']}"
            for msg in st.session_state.messages
        ])
        (drop_path / "conversation-history.md").write_text(conversation_md, encoding="utf-8")

        # Set session state to trigger research
        st.session_state.current_plan = plan
        st.session_state.current_drop_id = drop_id
        st.session_state.research_in_progress = True

        # Update drop state
        st.session_state.state_manager.update_drop_state(drop_id, "researching")

    def _show_mode_selector(self):
        """Show research mode selector before first message."""

        st.markdown("### Welcome to GTM Factory")
        st.markdown("Choose your research mode to get started:")

        # Center the mode selector cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            **ICP Validation**

            Validate your Ideal Customer Profile with:
            - Fit scoring (A/B/C/D tiers)
            - Intent signal identification
            - Clay-executable targeting criteria

            Best for: Early-stage companies, new markets, hypothesis testing
            """)
            if st.button("Start ICP Validation", key="mode_icp", use_container_width=True):
                st.session_state.research_mode = "icp-validation"
                st.rerun()

        with col2:
            st.markdown("""
            **GTM Execution**

            Validate go-to-market strategy with:
            - Channel validation
            - Messaging research
            - Execution playbooks

            Best for: Post-ICP companies ready to scale

            *Coming soon*
            """)
            # Disabled until implemented
            st.button("Start GTM Execution", key="mode_gtm", use_container_width=True, disabled=True)

        with col3:
            st.markdown("""
            **General Research**

            Flexible research orchestration for:
            - Market analysis
            - Competitive intelligence
            - Custom hypotheses

            Best for: Exploratory research, custom needs
            """)
            if st.button("Start General Research", key="mode_general", use_container_width=True):
                st.session_state.research_mode = "general"
                st.rerun()

        st.divider()
        st.caption("Your mode selection will be saved with this session. You can't change it later.")
