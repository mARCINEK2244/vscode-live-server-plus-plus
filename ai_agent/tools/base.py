from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ToolParameter(BaseModel):
    """Definition of a tool parameter."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum_values: Optional[List[str]] = None

class ToolResult(BaseModel):
    """Result returned by a tool execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseTool(ABC):
    """Base class for all agent tools."""
    
    def __init__(self):
        self.name = getattr(self, 'name', self.__class__.__name__.lower())
        self.description = getattr(self, 'description', 'No description provided')
        self.parameters = getattr(self, 'parameters', [])
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate that required parameters are provided."""
        for param in self.parameters:
            if param.required and param.name not in params:
                return False
        return True
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool schema for function calling."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    param.name: {
                        "type": param.type,
                        "description": param.description,
                        **({"enum": param.enum_values} if param.enum_values else {})
                    }
                    for param in self.parameters
                },
                "required": [param.name for param in self.parameters if param.required]
            }
        }
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"