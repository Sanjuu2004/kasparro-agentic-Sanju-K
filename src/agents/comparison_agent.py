from typing import Dict, Any
from .base import BaseAgent
from ..core.templates import TemplateFactory
from ..core.state import state_manager


class ComparisonPageAgent(BaseAgent):
    """Generates comparison page between products"""
    
    def __init__(self):
        super().__init__("comparison_v1", "Comparison Page Agent")
        self.required_state_fields = ["product_data", "product_b_data"]
        self.dependencies = ["product_b_creation"]
    
    async def _execute_impl(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparison page"""
        state = state_manager.get_state()
        
        # Prepare products for comparison
        products = [
            {
                "name": state.product_data.name,
                "concentration": state.product_data.concentration,
                "skin_type": state.product_data.skin_type,
                "key_ingredients": state.product_data.key_ingredients,
                "benefits": state.product_data.benefits,
                "price": state.product_data.price,
                "type": "Main Product"
            },
            {
                **state.product_b_data,
                "type": "Comparison Product"
            }
        ]
        
        # Render comparison template
        comparison_page = TemplateFactory.render_template(
            "comparison_v1",
            {
                "products": products,
                "product_data": state.product_data,
                "context": context
            }
        )
        
        # Update state
        state_manager.update_state(comparison_page=comparison_page)
        
        return {
            "comparison_generated": True,
            "products_compared": len(products),
            "comparison_points": len(comparison_page.get("comparison_points", [])),
            "recommendation": comparison_page.get("recommendation", "")[:100] + "..."
        }