"""
The module defines a Pydantic schema for managing custom requests.
"""

from typing import Any, Dict
from pydantic import BaseModel


class ExecuteRequest(BaseModel):
    """
    Request schema for to execute an action with specified parameters.
    Includes an action name and a dictionary of parameters to be passed
    to the action.
    """
    action: str
    params: Dict[str, Any]
