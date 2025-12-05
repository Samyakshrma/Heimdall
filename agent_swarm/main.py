from dotenv import load_dotenv
from src.graph import create_heimdall_graph

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print(">>> Initializing Heimdall Auto-SRE Swarm <<<")
    app = create_heimdall_graph()
    
    config = {"recursion_limit": 100}
    initial_state = {"messages": []}

    try:
        # Run the graph stream
        for event in app.stream(initial_state, config):
            pass # Logs are handled within nodes
    except KeyboardInterrupt:
        print("\n>>> Swarm stopped by user <<<")