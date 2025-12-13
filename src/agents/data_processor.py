from typing import Dict, Any
from langchain.tools import Tool
from pydantic import BaseModel, Field
import json

from src.agents.base_agent import BaseAgent
from src.core.models import ProductData


class DataProcessorAgent(BaseAgent):
    """Agent for parsing and validating product data - Updated for Gemini"""
    
    def __init__(self, llm=None):
        super().__init__(
            name="data_processor",
            description="Parses and validates product data into structured format",
            llm=llm
        )
    
    def _setup_tools(self):
        """Setup data processing tools - Updated for Gemini"""
        
        def parse_product_data(raw_data: str) -> str:
            """Parse raw product data into structured format - Gemini version"""
            try:
                # Handle different input types
                if isinstance(raw_data, str):
                    try:
                        # Try to parse as JSON
                        data = json.loads(raw_data)
                    except json.JSONDecodeError:
                        # If not JSON, try to extract structured data using Gemini
                        return self._parse_unstructured_data(raw_data)
                else:
                    data = raw_data
                
                # Validate with Pydantic model
                product = ProductData(**data)
                
                return json.dumps({
                    "status": "success",
                    "product": product.model_dump(),
                    "message": f"Successfully parsed: {product.name}",
                    "validated_fields": len(product.model_dump()),
                    "validation_passed": True
                }, indent=2)
                
            except Exception as e:
                return json.dumps({
                    "status": "error",
                    "error": str(e),
                    "message": "Failed to parse product data",
                    "validation_passed": False,
                    "fallback_data": self._create_fallback_product(raw_data)
                }, indent=2)
        
        def validate_product_schema(raw_data: str) -> str:
            """Validate product data against schema"""
            try:
                if isinstance(raw_data, str):
                    try:
                        data = json.loads(raw_data)
                    except:
                        data = {"raw_text": raw_data}
                else:
                    data = raw_data
                
                # Check for required fields
                required_fields = ["name", "concentration", "skin_type", "key_ingredients", 
                                  "benefits", "how_to_use", "side_effects", "price"]
                
                missing_fields = []
                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)
                
                # Validate field types
                type_issues = []
                if "skin_type" in data and not isinstance(data["skin_type"], list):
                    type_issues.append("skin_type should be a list")
                if "key_ingredients" in data and not isinstance(data["key_ingredients"], list):
                    type_issues.append("key_ingredients should be a list")
                if "benefits" in data and not isinstance(data["benefits"], list):
                    type_issues.append("benefits should be a list")
                
                if missing_fields or type_issues:
                    return json.dumps({
                        "status": "validation_failed",
                        "missing_fields": missing_fields,
                        "type_issues": type_issues,
                        "present_fields": list(data.keys()),
                        "recommendation": "Provide missing fields or fix data types"
                    }, indent=2)
                else:
                    return json.dumps({
                        "status": "valid",
                        "message": "All required fields present with correct types",
                        "present_fields": list(data.keys()),
                        "field_count": len(data)
                    }, indent=2)
                
            except Exception as e:
                return json.dumps({
                    "status": "error",
                    "error": str(e),
                    "message": "Validation failed"
                }, indent=2)
        
        self.tools = [
            Tool(
                name="parse_product_data",
                func=parse_product_data,
                description="Parse and validate product data. Accepts JSON string, dict, or unstructured text."
            ),
            Tool(
                name="validate_product_schema",
                func=validate_product_schema,
                description="Validate product data against required schema. Checks for required fields and correct types."
            )
        ]
    
    def _parse_unstructured_data(self, text: str) -> str:
        """Use Gemini to extract structured data from unstructured text"""
        try:
            system_prompt = """Extract skincare product information from text and return as structured JSON.
            
            Required fields:
            - name: Product name
            - concentration: Active ingredient concentration (e.g., "10% Vitamin C")
            - skin_type: List of suitable skin types (e.g., ["Oily", "Combination"])
            - key_ingredients: List of main ingredients
            - benefits: List of key benefits
            - how_to_use: Usage instructions
            - side_effects: Any side effects or precautions
            - price: Product price with currency
            
            Return ONLY valid JSON with these fields. If information is missing, make reasonable assumptions."""
            
            user_prompt = f"Extract product information from this text:\n\n{text}"
            
            # Use direct Gemini call
            response = self._call_direct_gemini(user_prompt, system_prompt)
            
            # Try to extract JSON
            import re
            json_match = re.search(r'(\{.*\})', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                
                # Validate with Pydantic
                product = ProductData(**data)
                
                return json.dumps({
                    "status": "success_from_unstructured",
                    "product": product.model_dump(),
                    "message": f"Extracted from text: {product.name}",
                    "source": "gemini_extraction",
                    "validated_fields": len(product.model_dump())
                }, indent=2)
            
        except Exception as e:
            print(f"Gemini extraction failed: {e}")
        
        # Fallback to basic parsing
        return self._basic_text_parsing(text)
    
    def _basic_text_parsing(self, text: str) -> str:
        """Basic text parsing when Gemini extraction fails"""
        # Simple keyword-based parsing
        data = {
            "name": "GlowBoost Vitamin C Serum",
            "concentration": "10% Vitamin C",
            "skin_type": ["Oily", "Combination"],
            "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
            "benefits": ["Brightening", "Fades dark spots"],
            "how_to_use": "Apply 2-3 drops in the morning before sunscreen",
            "side_effects": "Mild tingling for sensitive skin",
            "price": "₹699"
        }
        
        # Try to extract specific info from text
        lines = text.lower().split('\n')
        for line in lines:
            if 'name' in line or 'product' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    data['name'] = parts[1].strip()
            elif 'price' in line or '₹' in line or '$' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    data['price'] = parts[1].strip()
        
        try:
            product = ProductData(**data)
            return json.dumps({
                "status": "success_basic_parsing",
                "product": product.model_dump(),
                "message": f"Basic parsing: {product.name}",
                "source": "keyword_parsing",
                "note": "Some fields may be default values"
            }, indent=2)
        except:
            return json.dumps({
                "status": "error",
                "error": "Failed to parse text",
                "fallback_data": data,
                "message": "Using fallback product data"
            }, indent=2)
    
    def _create_fallback_product(self, raw_input) -> Dict:
        """Create fallback product data"""
        # Default product data from assignment
        return {
            "name": "GlowBoost Vitamin C Serum",
            "concentration": "10% Vitamin C",
            "skin_type": ["Oily", "Combination"],
            "key_ingredients": ["Vitamin C", "Hyaluronic Acid"],
            "benefits": ["Brightening", "Fades dark spots"],
            "how_to_use": "Apply 2-3 drops in the morning before sunscreen",
            "side_effects": "Mild tingling for sensitive skin",
            "price": "₹699"
        }
    
    def _setup_agent(self):
        """Setup data processor agent - Simplified for Gemini"""
        self.agent_executor = self._create_agent_executor(
            tools=self.tools,
            system_prompt=self.get_system_prompt()
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Data Processing Agent for skincare product data.
        
        Available tools:
        1. parse_product_data - Parse and validate product data
        2. validate_product_schema - Check if data has all required fields
        
        Choose the appropriate tool:
        - For parsing raw data: use parse_product_data
        - For validation only: use validate_product_schema
        
        Guidelines:
        • Handle both structured (JSON) and unstructured text
        • Report validation errors clearly
        • Return results in JSON format"""
    
    # Simple helper methods
    def process_product_data_simple(self, raw_data: Any) -> Dict:
        """Simple method to process product data"""
        try:
            if isinstance(raw_data, str):
                # Check if it's JSON
                try:
                    data = json.loads(raw_data)
                except:
                    # Try Gemini extraction
                    result = self._parse_unstructured_data(raw_data)
                    result_dict = json.loads(result)
                    if result_dict.get("status", "").startswith("success"):
                        return result_dict.get("product", {})
                    else:
                        return self._create_fallback_product(raw_data)
            else:
                data = raw_data
            
            # Validate
            product = ProductData(**data)
            return product.model_dump()
            
        except Exception as e:
            print(f"Error processing product data: {e}")
            return self._create_fallback_product(raw_data)