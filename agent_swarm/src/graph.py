from langgraph.graph import StateGraph, END
from src.state import IncidentState
from src.nodes import monitor_node, triage_node, diagnose_node, action_node, verify_node

def create_heimdall_graph():
    workflow = StateGraph(IncidentState)

    # Add Nodes
    workflow.add_node("monitor", monitor_node)
    workflow.add_node("triage", triage_node)
    workflow.add_node("diagnose", diagnose_node)
    workflow.add_node("action", action_node)
    workflow.add_node("verify", verify_node)

    # Set Entry
    workflow.set_entry_point("monitor")

    # Conditional Logic
    def check_alert(state):
        return "monitor" if state["is_healthy"] else "triage"
    
    def check_resolution(state):
        return "monitor" if state["incident_resolved"] else END

    # Edges
    workflow.add_conditional_edges("monitor", check_alert)
    workflow.add_edge("triage", "diagnose")
    workflow.add_edge("diagnose", "action")
    workflow.add_edge("action", "verify")
    workflow.add_conditional_edges("verify", check_resolution)

    return workflow.compile()