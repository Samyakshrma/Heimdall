import os
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.tools import ALL_TOOLS

# --- LLM Initialization (Azure) ---
# We use AzureChatOpenAI instead of ChatOpenAI
llm = AzureChatOpenAI(
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
    openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    temperature=0
)

def build_agent_executor(tools, system_prompt):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    agent = create_openai_tools_agent(llm, tools, prompt)
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
triage_executor = build_agent_executor([ALL_TOOLS[2]], TRIAGE_PROMPT) # get_recent_commits
diagnose_executor = build_agent_executor([ALL_TOOLS[3]], DIAGNOSE_PROMPT) # get_commit_diff
action_executor = build_agent_executor([ALL_TOOLS[4], ALL_TOOLS[5]], ACTION_PROMPT) # revert, slack