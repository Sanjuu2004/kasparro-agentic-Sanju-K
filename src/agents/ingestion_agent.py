from typing import Dict, Any
from .base import BaseAgent
from ..core.models import ProductData
from ..core.state import state_manager


class DataIngestionAgent(BaseAgent):
    """Parses and validates raw product data"""
    
    def __init__(self):
        super().__init__("ingestion_v1", "Data Ingestion Agent")
    
    async def _execute_impl(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw product data into structured model"""
        raw_data = context.get("raw_product_data")
        
        if not raw_data:
            raise ValueError("No raw_product_data provided in context")
        
        # Validate required fields
        required_fields = ["name", "concentration", "skin_type", "key_ingredients", 
                          "benefits", "how_to_use", "side_effects", "price"]
        
        missing_fields = [field for field in required_fields if field not in raw_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Convert to ProductData model (validates automatically)
        product_data = ProductData(**raw_data)
        
        # Update state (state manager already initialized this in orchestrator)
        # Just return the parsed data
        return {
            "product_parsed": True,
            "product_name": product_data.name,
            "fields_processed": len(required_fields),
            "validation_passed": True
        }