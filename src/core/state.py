from typing import Dict, Any, Optional
from contextvars import ContextVar
import json
from .models import SystemState, ProductData


class StateManager:
    """Manages pipeline state with context awareness"""
    
    def __init__(self):
        self._current_state: ContextVar[Optional[SystemState]] = ContextVar(
            'current_state', default=None
        )
        self._state_history: List[SystemState] = []
    
    def initialize_state(self, raw_product_data: Dict[str, Any]) -> SystemState:
        """Initialize state from raw product data"""
        product_data = ProductData(**raw_product_data)
        state = SystemState(product_data=product_data)
        self._current_state.set(state)
        self._state_history.append(state)
        return state
    
    def get_state(self) -> SystemState:
        """Get current state"""
        state = self._current_state.get()
        if state is None:
            raise RuntimeError("State not initialized")
        return state
    
    def update_state(self, **updates) -> SystemState:
        """Update state immutably"""
        current = self.get_state()
        new_state = SystemState(
            **{**current.__dict__, **updates}
        )
        self._current_state.set(new_state)
        self._state_history.append(new_state)
        return new_state
    
    def add_agent_message(self, message: AgentMessage):
        """Add message to state"""
        current = self.get_state()
        current.agent_messages.append(message)
        self._current_state.set(current)
    
    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get JSON serializable snapshot"""
        state = self.get_state()
        return {
            "product": state.product_data.model_dump(),
            "questions_count": len(state.generated_questions),
            "content_blocks": list(state.content_blocks.keys()),
            "faq_count": len(state.faq_items),
            "has_product_page": state.product_page is not None,
            "has_comparison_page": state.comparison_page is not None,
            "message_count": len(state.agent_messages),
            "error_count": len(state.errors)
        }


# Global state manager instance
state_manager = StateManager()