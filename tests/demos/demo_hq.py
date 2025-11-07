"""
Quick demo script to interact with HQ Orchestrator.

Run this to test the conversational Socratic questioning flow.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from core.hq.orchestrator import HQOrchestrator
from core.hq.context_extractor import ContextExtractor
from core.hq.memory_manager import MemoryManager

# Load environment variables from .env file
load_dotenv()

def main():
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found in environment")
        print("Set it in your .env file or run:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        return

    # Setup
    project_path = Path(__file__).parent / "projects" / "demo-company"
    session_id = "session-demo"

    print("🤖 GTM Factory - HQ Orchestrator Demo\n")
    print("=" * 60)
    print("This is a simple demo to test the Socratic questioning flow.")
    print("The HQ will ask clarifying questions to understand your research needs.")
    print("=" * 60)
    print()

    # Initialize
    hq = HQOrchestrator(api_key, project_path, session_id)
    memory = MemoryManager(project_path, session_id)

    print("💡 Tip: Type 'quit' to exit, 'save' to save conversation\n")

    # Conversation loop
    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == 'quit':
            print("\n👋 Goodbye!")
            break

        if user_input.lower() == 'save':
            # Save conversation
            conv_path = memory.save_conversation_history(hq.get_conversation_history())
            print(f"\n💾 Conversation saved to: {conv_path}\n")
            continue

        # Stream HQ's response
        print("\nHQ: ", end="", flush=True)

        for chunk in hq.chat_stream(user_input):
            print(chunk, end="", flush=True)

        print("\n")  # New line after response

    # Save conversation on exit
    print("\n💾 Saving conversation before exit...")
    memory.save_conversation_history(hq.get_conversation_history())
    print(f"📂 Saved to: {project_path / 'sessions' / session_id}")

    # Extract context
    print("\n🔍 Extracting user context...")
    extractor = ContextExtractor(api_key)
    context = extractor.extract(hq.get_conversation_history())

    context_path = memory.save_user_context(context.to_markdown())
    print(f"✅ Context saved to: {context_path}")

    print("\n📊 Summary:")
    print(f"   Strategic WHY: {context.strategic_why[:100]}...")
    print(f"   Decision Context: {context.decision_context[:100]}...")

if __name__ == "__main__":
    main()
