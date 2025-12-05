import operator
from typing import List, Dict, Optional, Annotated
from typing_extensions import TypedDict

class IncidentState(TypedDict):
    incident_id: str
    is_healthy: bool
    alert_logs: str
    potential_culprits: List[Dict] 
    confirmed_culprit_hash: Optional[str]
    diagnosis: str
    fix_strategy: str
    fix_output: str
    incident_resolved: bool
    # 'operator.add' appends new messages to the history rather than overwriting
    messages: Annotated[list, operator.add]