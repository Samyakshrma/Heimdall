import os
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.tools import ALL_TOOLS

# --- STANDARD IMPORT ---
from langchain.agents import AgentExecutor, create_tool_calling_agent

# --- LLM Initialization (Azure) ---
llm = AzureChatOpenAI(
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
    openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    temperature=0
)

def build_agent_executor(tools, system_prompt):
    # CRITICAL FIX: Added 'agent_scratchpad' placeholder
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"), 
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # We return the executor, which runs the agent loop
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- Agent Definitions ---

TRIAGE_PROMPT = """You are a Triage SRE. An alert has triggered.
Find the bad commit. Use 'get_recent_commits'. 
Analyze messages and timestamps against the alert logs."""

DIAGNOSE_PROMPT = """You are a Diagnosis Engineer. 
Use 'get_commit_diff' on the potential culprits.
Confirm the exact cause. 
Output a final diagnosis explaining why the commit broke the app."""

ACTION_PROMPT = """You are the Action SRE.
1. Post to Slack about the fix.
2. Use 'execute_revert_and_redeploy' with the confirmed hash.
3. Report the result."""

# Executors
triage_executor = build_agent_executor([ALL_TOOLS[2]], TRIAGE_PROMPT) 
diagnose_executor = build_agent_executor([ALL_TOOLS[3]], DIAGNOSE_PROMPT) 
action_executor = build_agent_executor([ALL_TOOLS[4], ALL_TOOLS[5]], ACTION_PROMPT)