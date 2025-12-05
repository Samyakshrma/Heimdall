import time
from langchain_core.messages import HumanMessage
from src.state import IncidentState
from src.tools import check_app_health, get_docker_logs, get_recent_commits, post_slack_message
from src.agents import triage_executor, diagnose_executor, action_executor

def monitor_node(state: IncidentState):
    status = check_app_health.invoke({})
    if "healthy" in status:
        print("--- MONITOR: App is healthy ---")
        return {"is_healthy": True, "messages": []}
    
    print("--- MONITOR: ALERT! App is down ---")
    logs = get_docker_logs.invoke({})
    msg = HumanMessage(content=f"ALERT: {status}\nLOGS:\n{logs}")
    return {"is_healthy": False, "alert_logs": logs, "messages": [msg]}

def triage_node(state: IncidentState):
    print("--- TRIAGE ---")
    response = triage_executor.invoke({"messages": state['messages']})
    
    # Heuristic: Grab top 2 commits for diagnosis
    commits = get_recent_commits.invoke({})
    potential_culprits = commits[:2]
    
    msg = HumanMessage(content=f"Triage Findings: {response['output']}")
    return {"potential_culprits": potential_culprits, "messages": [msg]}

def diagnose_node(state: IncidentState):
    print("--- DIAGNOSE ---")
    response = diagnose_executor.invoke({"messages": state['messages']})
    
    # Heuristic: The most recent commit (index 0) is usually the culprit
    bad_hash = state['potential_culprits'][0]['hash']
    
    msg = HumanMessage(content=response['output'])
    return {"confirmed_culprit_hash": bad_hash, "diagnosis": response['output'], "messages": [msg]}

def action_node(state: IncidentState):
    print("--- ACTION ---")
    task = HumanMessage(content=f"Fix Issue. Culprit: {state['confirmed_culprit_hash']}")
    response = action_executor.invoke({"messages": [task]})
    
    msg = HumanMessage(content=f"Fix Report: {response['output']}")
    return {"fix_output": response['output'], "messages": [msg]}

def verify_node(state: IncidentState):
    print("--- VERIFYING FIX (Waiting 20s) ---")
    time.sleep(20)
    status = check_app_health.invoke({})
    
    if "healthy" in status:
        post_slack_message.invoke("✅ Incident Resolved. Service restored.")
        return {"incident_resolved": True}
    
    post_slack_message.invoke("❌ Fix Failed. Human intervention required.")
    return {"incident_resolved": False}