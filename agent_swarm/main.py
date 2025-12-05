import os
from dotenv import load_dotenv

# --- CRITICAL: Load env vars BEFORE importing src modules ---
# If you import src.graph first, agents.py runs immediately and fails
# because keys aren't loaded yet.
load_dotenv() 

# Now it is safe to import your project code
from src.graph import create_heimdall_graph

if __name__ == "__main__":
    print(">>> Initializing Heimdall Auto-SRE Swarm <<<")
    
    # Optional: Debug check to prove keys are loaded
    if not os.environ.get("AZURE_OPENAI_API_KEY"):
        print("❌ ERROR: AZURE_OPENAI_API_KEY is missing. Check your .env file.")
        exit(1)

    app = create_heimdall_graph()
    
    config = {"recursion_limit": 500} # Change 100 to 500
    initial_state = {"messages": []}

    try:
        # Run the graph stream
        for event in app.stream(initial_state, config):
            pass # Logs are handled within nodes
    except KeyboardInterrupt:
        print("\n>>> Swarm stopped by user <<<")