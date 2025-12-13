from typing import TypedDict, Annotated, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage

# Try different import methods for add_messages
try:
    # Method 1: Newer versions
    from langgraph.graph import add_messages
except ImportError:
    try:
        # Method 2: Older versions
        from langgraph.graph.message import add_messages
    except ImportError:
        # Method 3: Define our own
        from typing import Any
        def add_messages(left: List[Any], right: List[Any]) -> List[Any]:
            return left + right


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