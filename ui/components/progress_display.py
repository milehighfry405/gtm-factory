"""
Progress Display Component - Shows research and generator progress.
"""

import streamlit as st
import asyncio
from pathlib import Path


class ProgressDisplay:
    """
    Display progress for research and generator execution.

    Shows:
    - Researcher statuses (searching, analyzing, writing)
    - Generator statuses (synthesizing, analyzing)
    - Real-time updates
    """

    def render(self):
        """Render progress display."""

        # Only show if research in progress
        if not st.session_state.get("research_in_progress", False):
            return

        st.divider()

        # Header with stop button
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader("Research Progress")
        with col2:
            if st.button("⏹️ Stop Research", type="secondary", use_container_width=True):
                st.session_state.cancel_research = True
                st.warning("Stopping research...")
                st.rerun()

        # Execute research if not already done
        if st.session_state.get("current_plan") and not st.session_state.get("research_complete", False):
            self._execute_research_async()

    def _execute_research_async(self):
        """Execute research asynchronously with progress updates."""

        plan = st.session_state.current_plan
        drop_id = st.session_state.current_drop_id

        session_path = Path(f"projects/sessions/{st.session_state.session_id}")
        drop_path = session_path / "drops" / drop_id

        # Get researcher count for tiles
        researchers = plan.get("researchers_assigned", plan.get("researchers", []))
        num_researchers = len(researchers)

        # Create researcher tile placeholders
        st.write("### 🔬 Researchers")
        researcher_tiles = {}

        if num_researchers > 0:
            cols = st.columns(min(num_researchers, 3))  # Max 3 per row
            for idx, researcher_config in enumerate(researchers):
                researcher_id = researcher_config.get("id", f"researcher-{idx+1}")
                col_idx = idx % 3
                with cols[col_idx]:
                    # Create tile container
                    with st.container():
                        st.markdown(f"**{researcher_id}**")
                        researcher_tiles[researcher_id] = st.empty()
                        researcher_tiles[researcher_id].info("⏳ Queued...")

        # Generator status placeholder
        st.write("### 📊 Synthesis")
        generator_status = st.empty()

        def on_research_progress(researcher_id, status, message):
            """Callback for research progress."""
            if researcher_id in researcher_tiles:
                # Update specific researcher tile
                if "complete" in status.lower() or "done" in status.lower():
                    researcher_tiles[researcher_id].success(f"✅ {status}")
                elif "error" in status.lower() or "fail" in status.lower():
                    researcher_tiles[researcher_id].error(f"❌ {status}")
                else:
                    researcher_tiles[researcher_id].info(f"🔄 {status}")

        def on_generator_status(status, message):
            """Callback for generator progress."""
            generator_status.info(f"🔄 {message}")

        try:
            # Check for cancellation before starting
            if st.session_state.get("cancel_research", False):
                self._handle_cancellation(drop_id, generator_status)
                return

            # Execute research (async) with mission briefing transformation
            with st.spinner("Executing research..."):
                outputs = asyncio.run(
                    st.session_state.researcher_adapter.execute_research_plan(
                        plan=plan,
                        drop_path=drop_path,
                        research_mode=st.session_state.get("research_mode", "general"),
                        hypothesis=plan.get("hypothesis", ""),
                        on_progress=on_research_progress,
                        cancellation_flag=lambda: st.session_state.get("cancel_research", False)
                    )
                )

            # Check for cancellation after research (before generators)
            if st.session_state.get("cancel_research", False):
                self._handle_cancellation(drop_id, generator_status)
                return

            generator_status.success(f"✅ Research complete ({len(outputs)} researchers)")

            # Update drop state
            st.session_state.state_manager.update_drop_state(drop_id, "synthesizing")

            # Run generators
            with st.spinner("Synthesizing findings..."):
                # Synthesize
                latest_md = st.session_state.generator_adapter.synthesize_drop(
                    session_path=session_path,
                    drop_id=drop_id,
                    on_status=on_generator_status
                )

                # Critical analysis
                critical_md = st.session_state.generator_adapter.analyze_drop(
                    session_path=session_path,
                    drop_id=drop_id,
                    on_status=on_generator_status
                )

                # Metadata
                metadata = st.session_state.generator_adapter.generate_metadata(
                    session_path=session_path,
                    on_status=on_generator_status
                )

            generator_status.success("✅ Synthesis and analysis complete")

            # Update drop state
            st.session_state.state_manager.update_drop_state(drop_id, "complete")

            # Load context into HQ
            st.session_state.hq_adapter.load_drop_context(drop_id)

            # Mark complete
            st.session_state.research_in_progress = False
            st.session_state.research_complete = True
            st.session_state.current_drop_id = None
            st.session_state.current_plan = None

            # Add HQ summary to conversation
            summary_message = f"Research complete for {drop_id}. I've analyzed the findings and identified some gaps. Let's discuss what we learned."

            st.session_state.messages.append({
                "role": "assistant",
                "content": summary_message
            })

            st.success("🎉 Research drop complete! HQ is ready to discuss findings.")
            st.rerun()

        except Exception as e:
            # Check if this was a cancellation vs real error
            if st.session_state.get("cancel_research", False):
                self._handle_cancellation(drop_id, generator_status)
            else:
                st.error(f"Research failed: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
                st.session_state.state_manager.update_drop_state(drop_id, "failed")
                st.session_state.research_in_progress = False

    def _handle_cancellation(self, drop_id: str, status_placeholder):
        """Handle research cancellation."""
        # Mark drop as cancelled
        st.session_state.state_manager.update_drop_state(drop_id, "cancelled")

        # Clean up state
        st.session_state.research_in_progress = False
        st.session_state.current_drop_id = None
        st.session_state.current_plan = None
        st.session_state.cancel_research = False

        # Show confirmation
        status_placeholder.success("✅ Research stopped - drop marked as cancelled")
        st.info("Research has been stopped. You can start a new research session when ready.")
        st.rerun()
