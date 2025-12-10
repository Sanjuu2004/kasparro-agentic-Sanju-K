from typing import Dict, Any
from .base import BaseAgent
from ..core.templates import TemplateFactory
from ..core.state import state_manager


class ProductPageAgent(BaseAgent):
    """Generates product description page"""
    
    def __init__(self):
        super().__init__("product_page_v1", "Product Page Agent")
        self.required_state_fields = ["product_data"]
    
    async def _execute_impl(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product page using template"""
        state = state_manager.get_state()
        
        # Render product page template
        product_page = TemplateFactory.render_template(
            "product_page_v1",
            {
                "product_data": state.product_data,
                "context": context
            }
        )
        
        # Update state
        state_manager.update_state(product_page=product_page)
        
        return {
            "page_generated": True,
            "page_sections": len(product_page),
            "title": product_page.get("title", "Product Page"),
            "sections": list(product_page.keys())
        }