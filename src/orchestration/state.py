from typing import TypedDict, Annotated, List, Optional, Dict, Any
from pydantic import BaseModel
from langchain_core.messages import BaseMessage


# For newer versions of langgraph, use add_messages differently
try:
    from langgraph.graph import add_messages
except ImportError:
    # Fallback for older versions
    from langgraph.graph.message import add_messages


class ContentGenerationState(TypedDict):
    """State for LangGraph workflow with typed fields"""
    # Messages for workflow communication
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Product data
    raw_product_data: Optional[Dict[str, Any]]
    parsed_product_data: Optional[Dict[str, Any]]
    
    # Generated content
    generated_questions: Optional[List[Dict[str, Any]]]
    fictional_product: Optional[Dict[str, Any]]
    faq_content: Optional[List[Dict[str, Any]]]
    product_page_content: Optional[Dict[str, Any]]
    comparison_content: Optional[Dict[str, Any]]
    
    # Workflow metadata
    errors: List[str]
    current_step: str
    completed_steps: List[str]
    
    # Final outputs
    output_files: List[str]