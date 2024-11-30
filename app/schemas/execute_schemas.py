"""
The module defines a Pydantic schema for managing execute requests.
Includes a schema for specifying an action and associated parameters.
"""

from typing import Any, Dict
from pydantic import BaseModel


class ExecuteRequest(BaseModel):
    """
    Pydantic schema for a request to execute an action with specified
    parameters. Includes an action name and a dictionary of parameters
    to be passed to the action.
    """
    action: str
    params: Dict[str, Any]
