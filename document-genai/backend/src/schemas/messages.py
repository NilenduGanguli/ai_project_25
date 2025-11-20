"""
Message classes for compatibility with LangChain-style interfaces
"""
from typing import Union, List, Dict, Any


class HumanMessage:
    """Human message for chat interfaces"""
    
    def __init__(self, content: Union[str, List[Dict[str, Any]]]):
        self.content = content


class SystemMessage:
    """System message for chat interfaces"""
    
    def __init__(self, content: str):
        self.content = content