import json
from typing import Dict, Any, List, Optional
from pydantic import ValidationError

from src.core.models import ProductData, FAQItem, ProductPage, ComparisonPage


def validate_product_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate product data against Pydantic model"""
    try:
        product = ProductData(**data)
        return {
            "valid": True,
            "product": product.model_dump(),
            "errors": []
        }
    except ValidationError as e:
        return {
            "valid": False,
            "product": None,
            "errors": [str(err) for err in e.errors()]
        }


def validate_json_output(filepath: str, model_type: str) -> Dict[str, Any]:
    """Validate JSON output files against expected models"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if model_type == "faq":
            if "faq_items" in data:
                for item in data["faq_items"]:
                    FAQItem(**item)
            return {"valid": True, "model": "FAQ", "item_count": len(data.get("faq_items", []))}
        
        elif model_type == "product_page":
            ProductPage(**data)
            return {"valid": True, "model": "ProductPage", "sections": len(data)}
        
        elif model_type == "comparison_page":
            ComparisonPage(**data)
            return {"valid": True, "model": "ComparisonPage", "products": len(data.get("products", []))}
        
        else:
            return {"valid": False, "error": f"Unknown model type: {model_type}"}
            
    except Exception as e:
        return {"valid": False, "error": str(e)}


def format_for_llm(data: Dict[str, Any]) -> str:
    """Format data for LLM consumption"""
    try:
        return json.dumps(data, indent=2)
    except:
        return str(data)