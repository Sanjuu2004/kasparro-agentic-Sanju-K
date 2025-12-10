from typing import Dict, Any
import random
from .base import BaseAgent
from ..core.state import state_manager


class ProductBCreationAgent(BaseAgent):
    """Creates a fictional product B for comparison"""
    
    def __init__(self):
        super().__init__("product_b_v1", "Product B Creation Agent")
        self.required_state_fields = ["product_data"]
    
    async def _execute_impl(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create fictional product B"""
        state = state_manager.get_state()
        product_a = state.product_data
        
        # Create fictional Product B with different characteristics
        product_b = {
            "name": "RadiantSkin Vitamin C + E Serum",
            "concentration": "5% Vitamin C + 1% Vitamin E",
            "skin_type": ["Dry", "Normal", "Sensitive"],
            "key_ingredients": ["Vitamin C", "Vitamin E", "Ferulic Acid"],
            "benefits": ["Antioxidant Protection", "Hydration", "Reduces Inflammation"],
            "how_to_use": "Apply 3-4 drops in morning and evening after cleansing",
            "side_effects": "Rare irritation in extremely sensitive skin",
            "price": "₹899"
        }
        
        # Update state
        state_manager.update_state(product_b_data=product_b)
        
        return {
            "product_b_created": True,
            "product_b_name": product_b["name"],
            "differentiation": {
                "price_difference": f"{product_b['price']} vs {product_a.price}",
                "ingredient_difference": f"{len(product_b['key_ingredients'])} vs {len(product_a.key_ingredients)} ingredients",
                "skin_type_focus": "Dry/Normal vs Oily/Combination"
            }
        }